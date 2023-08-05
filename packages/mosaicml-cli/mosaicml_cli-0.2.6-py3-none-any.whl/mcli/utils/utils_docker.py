"""Utils for accessing docker sdk"""
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Dict, Generator, List, Optional, Set, Tuple

import docker
from docker.errors import APIError

logger = logging.getLogger(__name__)

DEFAULT_PLATFORM = 'linux/amd64'


def load_docker_config(config_file: str) -> Dict[str, Optional[str]]:
    with open(config_file, encoding='utf8') as f:
        data = json.loads(f.read())

    if 'username' not in data:
        raise KeyError(f'Field \'username\' must be provided in {config_file}')
    if 'password' not in data:
        raise KeyError(f'Field \'password\' must be provided in {config_file}')

    config = {}
    for f in ('username', 'password', 'email', 'registry'):
        if f in data:
            config[f] = data[f]

    return config


def get_docker_client() -> docker.APIClient:
    """Get the docker client
    """
    return docker.from_env(assert_hostname=True)


def get_image_tags(client: docker.APIClient) -> Set[str]:
    """Gets all unique image tags available
    """
    tags = set()
    for image in client.images.list():
        for tag in image.tags:
            tags.add(tag)
    return tags


def _get_common_path(path1: Path, path2: Path) -> Optional[Path]:
    """Returns a common path of two paths if there is one
    """

    while path1 is not None:
        if str(path1) in ('.', '/'):
            break
        try:
            path2.relative_to(path1)
            return path1
        except ValueError:
            path1 = path1.parent

    return None


@dataclass
class Dockerfile:
    """Abstracts components of a dockerfile to build
    """

    image: str
    base_image: str
    args: Dict[str, str] = field(default_factory=dict)
    copy: List[str] = field(default_factory=list)
    path: Optional[str] = None

    def get_copy_command(self, directory: str) -> str:
        d = Path(directory)

        path = Path(self.path or '.')
        common = _get_common_path(path, d)
        if common is not None:
            # import pdb; pdb.set_trace()
            docker_dir = path / d.relative_to(*common.parts)
        else:
            docker_dir = path / Path(directory)

        return f'COPY {directory} {docker_dir}'

    @property
    def contents(self) -> str:
        """Converts data into runnable Dockerfile text
        """
        lines = []
        lines.append(f'FROM --platform={DEFAULT_PLATFORM} {self.base_image}')

        for k, v in self.args.items():
            lines.append(f'ARG {k}="{v}"')

        for c in self.copy:
            lines.append(self.get_copy_command(c))

        contents = '\n'.join(lines)
        logger.debug(contents)
        return contents


def _push_stream_logger(log_generator: Generator[dict, None, None]) -> List[str]:
    last_status = None
    logs = []
    for log in log_generator:
        if 'aux' in log:
            logs.append(f'Pushed {log["aux"].get("Tag")} ({log["aux"].get("Digest")}), {log["aux"].get("Size")}bytes')
            break

        elif 'errorDetail' in log:
            raise RuntimeError(f'Failed to push to docker image: {log["errorDetail"]}')

        status = log.get('status', 'Unknown')
        if last_status == status:
            continue
        elif status == 'Unknown':
            logs.append(log)

        status_id = log.get('status_id', '')
        logs.append(f'Push status: {status} {status_id}')
        last_status = status

    return logs


def image_to_repo_tag(image: str) -> Tuple[str, Optional[str]]:
    """Disect repo and tag name from the image name
    """
    image, *potential_tag = image.split(':')

    if potential_tag:
        tag = potential_tag[0]
    else:
        tag = 'latest'

    return image, tag


class DockerImage:
    """Manage a docker image through the docker api
    """

    auth_config = None

    def __init__(
        self,
        base_image: str,
        dest_image: str,
        client: Optional[docker.APIClient] = None,
        config_file: Optional[str] = None,
    ):
        self.image = dest_image
        self.repo, self.tag = image_to_repo_tag(dest_image)
        self.base_image = base_image

        if client is None:
            client = get_docker_client()
        self.client: docker.APIClient = client

        if config_file is not None:
            self.auth_config = load_docker_config(config_file)

    def build(self, dockerfile: Dockerfile):
        """Builds a docker image using the dockerfile object provided
        """

        with NamedTemporaryFile('w') as temp:
            temp.write(dockerfile.contents)
            temp.seek(0)
            self.client.images.build(
                tag=self.image,
                path='.',  # relative path to look for dockerfile
                dockerfile=temp.name,
                nocache=False,
            )
            logger.debug(f"Docker image {self.image} created from {self.base_image}")

    def build_local_directories(self, directories: List[str], path: str) -> None:
        """Builds local directories into a docker image
        """
        logger.debug(f'Creating local directory image for {self.image}')
        self.build(dockerfile=Dockerfile(
            image=self.image,
            base_image=self.base_image,
            copy=directories,
            path=path,
        ))

    def push(self):
        """Pushes a docker image to a docker repo
        """
        try:
            if self._will_overwrite_important_tag():
                raise RuntimeError(
                    f'The image {self.image} already exists and pushing will overwrite this particular image tag. '
                    f'Either remove the tag from the image name ({self.repo}) '
                    'or update the tag in `push_image` in the YAML')

            args = {
                'repository': self.repo,
                'tag': self.tag,
                'auth_config': self.auth_config,
                # stream the push to catch any errors (not all raise an APIError)
                'stream': True,
                'decode': True,
            }
            for msg in _push_stream_logger(self.client.images.push(**args)):
                logger.debug(msg)
            logger.debug(f"Docker image {self.image} pushed")
        except APIError as e:
            if e.status_code == 403:
                # pylint: disable=raise-missing-from
                raise RuntimeError("Unauthorized docker push. Please ensure you are either logged in "
                                   "with `docker login` or have specified a valid `docker_config` in your YAML.")
            else:
                raise RuntimeError(e) from e

    def _will_overwrite_important_tag(self) -> bool:
        # allow overwrites to latest (default) tag
        if self.tag == 'latest':
            return False

        try:
            self.client.images.get_registry_data(self.image)
            return True
        except docker.errors.NotFound:
            return False

    def delete(self):
        """Delete the image locally
        """
        self.client.images.remove(self.image)
