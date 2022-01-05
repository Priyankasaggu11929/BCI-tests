import os
import shlex
from typing import List
from typing import Union

import pytest
from bci_tester.runtime_choice import DOCKER_SELECTED
from pytest_container import Container
from pytest_container import DerivedContainer
from pytest_container.runtime import LOCALHOST


DEFAULT_REGISTRY = "registry.suse.de"

#: The operating system version as present in /etc/os-release & various other
#: places
OS_VERSION = os.getenv("OS_VERSION", "15.3")

OS_MAJOR_VERSION, OS_SP_VERSION = (int(ver) for ver in OS_VERSION.split("."))

#: The SLES 15 pretty name (from /etc/os-release)
OS_PRETTY_NAME = os.getenv(
    "OS_PRETTY_NAME",
    f"SUSE Linux Enterprise Server {OS_MAJOR_VERSION} SP{OS_SP_VERSION}",
)

#: pytest mark to not run on non-x86_64 architectures because .Net is not
#: supported on these architectures
DOTNET_ARCH_SKIP_MARK = pytest.mark.skipif(
    LOCALHOST.system_info.arch != "x86_64",
    reason="The .Net containers are only available on x86_64",
)

assert (
    OS_MAJOR_VERSION == 15
), f"The tests are created for SLE 15 base images only, but got a request for SLE {OS_MAJOR_VERSION}"

#: the base URL under which all containers can be found on registry.suse.de
BASE_URL = f"{DEFAULT_REGISTRY}/suse/sle-{OS_MAJOR_VERSION}-sp{OS_SP_VERSION}/update/cr/totest/images"


BASE_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/suse/sle15:{OS_VERSION}",
)
MINIMAL_CONTAINER = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/minimal:{OS_VERSION}",
)
MICRO_CONTAINER = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/micro:{OS_VERSION}"
)

GO_1_16_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/golang:1.16"
)
GO_1_17_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/golang:1.17"
)

OPENJDK_11_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/openjdk:11"
)
OPENJDK_DEVEL_11_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/openjdk-devel:11"
)
NODEJS_12_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/nodejs:12"
)
NODEJS_14_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/nodejs:14"
)

PYTHON36_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/python:3.6"
)
PYTHON39_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/python:3.9"
)

DOTNET_SDK_3_1_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-sdk:3.1",
)
DOTNET_SDK_5_0_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-sdk:5.0",
)
DOTNET_SDK_6_0_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-sdk:6.0",
)

DOTNET_ASPNET_3_1_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-aspnet:3.1",
)
DOTNET_ASPNET_5_0_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-aspnet:5.0",
)
DOTNET_ASPNET_6_0_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-aspnet:6.0",
)

DOTNET_RUNTIME_3_1_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-runtime:3.1"
)
DOTNET_RUNTIME_5_0_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-runtime:5.0"
)
DOTNET_RUNTIME_6_0_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{BASE_URL}/bci/dotnet-runtime:6.0"
)

INIT_CONTAINER: Union[Container, DerivedContainer] = Container(
    url=f"{DEFAULT_REGISTRY}/suse/sle-15-sp3/update/cr/totest/images/bci/init:15.3",
    extra_launch_args=[
        "--privileged",
        "--tmpfs",
        "/tmp",
        "--tmpfs",
        "/run",
        "-v",
        "/sys/fs/cgroup:/sys/fs/cgroup:ro,z",
        "-e",
        "container=docker",
    ]
    if DOCKER_SELECTED
    else [],
    default_entry_point=True,
)


#
# !! IMPORTANT !!
# ===============
#
# All "base" containers which get pre-configured with the SLE_BCI repository
# should be put into this if branch so that their repository gets replaced on
# setting the `BCI_DEVEL_REPO` environment variable.
#
# We must not run any zypper commands here, as otherwise container-suseconnect
# will keep a ton of metadata of the fetched repositories (which is a lot on
# registered systems)
#
BCI_DEVEL_REPO = os.getenv("BCI_DEVEL_REPO")
if BCI_DEVEL_REPO is None:
    BCI_DEVEL_REPO = f"https://updates.suse.com/SUSE/Products/SLE-BCI/15-SP3/{LOCALHOST.system_info.arch}/product/"
else:
    REPLACE_REPO_CONTAINERFILE = f"RUN sed -i 's|baseurl.*|baseurl={BCI_DEVEL_REPO}|' /etc/zypp/repos.d/SLE_BCI.repo"

    (
        BASE_CONTAINER,
        GO_1_16_CONTAINER,
        GO_1_17_CONTAINER,
        OPENJDK_11_CONTAINER,
        OPENJDK_DEVEL_11_CONTAINER,
        NODEJS_12_CONTAINER,
        NODEJS_14_CONTAINER,
        PYTHON36_CONTAINER,
        PYTHON39_CONTAINER,
        DOTNET_SDK_3_1_CONTAINER,
        DOTNET_SDK_5_0_CONTAINER,
        DOTNET_SDK_6_0_CONTAINER,
        DOTNET_ASPNET_3_1_CONTAINER,
        DOTNET_ASPNET_5_0_CONTAINER,
        DOTNET_ASPNET_6_0_CONTAINER,
        DOTNET_RUNTIME_3_1_CONTAINER,
        DOTNET_RUNTIME_5_0_CONTAINER,
        DOTNET_RUNTIME_6_0_CONTAINER,
        INIT_CONTAINER,
    ) = (
        DerivedContainer(
            base=cont.url,
            containerfile=REPLACE_REPO_CONTAINERFILE,
            **{k: v for (k, v) in cont.__dict__.items() if k != "url"},
        )
        for cont in (
            BASE_CONTAINER,
            GO_1_16_CONTAINER,
            GO_1_17_CONTAINER,
            OPENJDK_11_CONTAINER,
            OPENJDK_DEVEL_11_CONTAINER,
            NODEJS_12_CONTAINER,
            NODEJS_14_CONTAINER,
            PYTHON36_CONTAINER,
            PYTHON39_CONTAINER,
            DOTNET_SDK_3_1_CONTAINER,
            DOTNET_SDK_5_0_CONTAINER,
            DOTNET_SDK_6_0_CONTAINER,
            DOTNET_ASPNET_3_1_CONTAINER,
            DOTNET_ASPNET_5_0_CONTAINER,
            DOTNET_ASPNET_6_0_CONTAINER,
            DOTNET_RUNTIME_3_1_CONTAINER,
            DOTNET_RUNTIME_5_0_CONTAINER,
            DOTNET_RUNTIME_6_0_CONTAINER,
            INIT_CONTAINER,
        )
    )


REPOCLOSURE_CONTAINER = DerivedContainer(
    base="registry.fedoraproject.org/fedora:latest",
    containerfile=r"""RUN dnf -y install 'dnf-command(repoclosure)'
RUN rm -f /etc/yum.repos.d/*repo
RUN echo $'[SLE_BCI] \n\
enabled=1 \n\
name="SLE BCI" \n\
autorefresh=0 \n\
baseurl="""
    + BCI_DEVEL_REPO
    + r""" \n\
priority=100' > /etc/yum.repos.d/SLE_BCI.repo
""",
)

DOTNET_CONTAINERS = [
    DOTNET_SDK_3_1_CONTAINER,
    DOTNET_SDK_5_0_CONTAINER,
    DOTNET_SDK_6_0_CONTAINER,
    DOTNET_ASPNET_3_1_CONTAINER,
    DOTNET_ASPNET_5_0_CONTAINER,
    DOTNET_ASPNET_6_0_CONTAINER,
    DOTNET_RUNTIME_3_1_CONTAINER,
    DOTNET_RUNTIME_5_0_CONTAINER,
    DOTNET_RUNTIME_6_0_CONTAINER,
]
CONTAINERS_WITH_ZYPPER: List[Union[Container, DerivedContainer]] = [
    BASE_CONTAINER,
    GO_1_16_CONTAINER,
    GO_1_17_CONTAINER,
    OPENJDK_11_CONTAINER,
    OPENJDK_DEVEL_11_CONTAINER,
    NODEJS_12_CONTAINER,
    NODEJS_14_CONTAINER,
    PYTHON36_CONTAINER,
    PYTHON39_CONTAINER,
    INIT_CONTAINER,
] + (DOTNET_CONTAINERS if LOCALHOST.system_info.arch == "x86_64" else [])

CONTAINERS_WITHOUT_ZYPPER: List[Union[DerivedContainer, Container]] = [
    MINIMAL_CONTAINER,
    MICRO_CONTAINER,
]

#: Containers that are directly pulled from registry.suse.de
ALL_CONTAINERS: List[Union[DerivedContainer, Container]] = (
    CONTAINERS_WITH_ZYPPER + CONTAINERS_WITHOUT_ZYPPER
)
