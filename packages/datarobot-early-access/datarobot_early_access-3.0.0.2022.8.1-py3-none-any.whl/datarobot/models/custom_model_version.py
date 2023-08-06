#
# Copyright 2021-2022 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import copy
import json
import os

import contextlib2
from requests_toolbelt import MultipartEncoder
import trafaret as t

from datarobot._compat import Int, String
from datarobot.enums import DEFAULT_MAX_WAIT, NETWORK_EGRESS_POLICY
from datarobot.errors import InvalidUsageError
from datarobot.models.api_object import APIObject
from datarobot.models.job import filter_feature_impact_result
from datarobot.models.validators import feature_impact_trafaret
from datarobot.utils import camelize
from datarobot.utils.pagination import unpaginate
from datarobot.utils.waiters import wait_for_async_resolution, wait_for_custom_resolution


class RequiredMetadataValue(APIObject):
    """Definition of a metadata key that custom models using this environment must define

    .. versionadded:: v2.26

    Attributes
    ----------
    field_name: str
        The required field names.  Required field names are defined by the
        environment's required_metadata_keys. This value will be added as an
        environment vairable when running custom models.
    value: str
        the value for the required field.
    """

    _converter = t.Dict({t.Key("field_name"): String(), t.Key("value"): String()})

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return "{}(field_name={!r}, value={!r})".format(
            self.__class__.__name__,
            self.field_name,
            self.value,
        )

    def _set_values(self, field_name, value):
        self.field_name = field_name
        self.value = value

    def to_dict(self):
        return self._converter.check({"field_name": self.field_name, "value": self.value})


class CustomModelFileItem(APIObject):
    """A file item attached to a DataRobot custom model version.

    .. versionadded:: v2.21

    Attributes
    ----------
    id: str
        id of the file item
    file_name: str
        name of the file item
    file_path: str
        path of the file item
    file_source: str
        source of the file item
    created_at: str, optional
        ISO-8601 formatted timestamp of when the version was created
    """

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("file_name"): String(),
            t.Key("file_path"): String(),
            t.Key("file_source"): String(),
            t.Key("created", optional=True) >> "created_at": String(),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(
        self,
        id,
        file_name,
        file_path,
        file_source,
        created_at=None,
    ):
        self.id = id
        self.file_name = file_name
        self.file_path = file_path
        self.file_source = file_source
        self.created_at = created_at


class CustomModelVersionDependencyBuild(APIObject):
    """Metadata about a DataRobot custom model version's dependency build

    .. versionadded:: v2.22

    Attributes
    ----------
    custom_model_id: str
        id of the custom model
    custom_model_version_id: str
        id of the custom model version
    build_status: str
        the status of the custom model version's dependency build
    started_at: str
        ISO-8601 formatted timestamp of when the build was started
    completed_at: str, optional
        ISO-8601 formatted timestamp of when the build has completed
    """

    _path = "customModels/{}/versions/{}/dependencyBuild/"
    _log_path = "customModels/{}/versions/{}/dependencyBuildLog/"

    _converter = t.Dict(
        {
            t.Key("custom_model_id"): String(),
            t.Key("custom_model_version_id"): String(),
            t.Key("build_status"): String(),
            t.Key("build_start") >> "started_at": String(),
            t.Key("build_end", optional=True) >> "completed_at": String(allow_blank=True),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return "{}(model={!r}, version={!r}, status={!r})".format(
            self.__class__.__name__,
            self.custom_model_id,
            self.custom_model_version_id,
            self.build_status,
        )

    def _set_values(  # pylint: disable=missing-function-docstring
        self,
        custom_model_id,
        custom_model_version_id,
        build_status,
        started_at,
        completed_at=None,
    ):
        self.custom_model_id = custom_model_id
        self.custom_model_version_id = custom_model_version_id
        self.build_status = build_status
        self.started_at = started_at
        self.completed_at = completed_at

    @classmethod
    def _update_server_data(cls, server_data, custom_model_id, custom_model_version_id):
        updated_data = copy.copy(server_data)
        updated_data.update(
            {"customModelId": custom_model_id, "customModelVersionId": custom_model_version_id}
        )
        return updated_data

    @classmethod
    def get_build_info(cls, custom_model_id, custom_model_version_id):
        """Retrieve information about a custom model version's dependency build

        .. versionadded:: v2.22

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model
        custom_model_version_id: str
            the id of the custom model version

        Returns
        -------
        CustomModelVersionDependencyBuild
            the dependency build information
        """
        url = cls._path.format(custom_model_id, custom_model_version_id)
        response = cls._client.get(url)
        server_data = response.json()
        updated_data = cls._update_server_data(
            server_data, custom_model_id, custom_model_version_id
        )
        return cls.from_server_data(updated_data)

    @classmethod
    def start_build(cls, custom_model_id, custom_model_version_id, max_wait=DEFAULT_MAX_WAIT):
        """Start the dependency build for a custom model version  dependency build

        .. versionadded:: v2.22

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model
        custom_model_version_id: str
            the id of the custom model version
        max_wait: int, optional
            max time to wait for a build completion.
            If set to None - method will return without waiting.
        """

        def build_complete(response):
            data = response.json()
            if data["buildStatus"] in ["success", "failed"]:
                updated_data = cls._update_server_data(
                    data, custom_model_id, custom_model_version_id
                )
                return cls.from_server_data(updated_data)
            return None

        url = cls._path.format(custom_model_id, custom_model_version_id)
        response = cls._client.post(url)

        if max_wait is None:
            server_data = response.json()
            updated_data = cls._update_server_data(
                server_data, custom_model_id, custom_model_version_id
            )
            return cls.from_server_data(updated_data)
        else:
            return wait_for_custom_resolution(cls._client, url, build_complete, max_wait)

    def get_log(self):
        """Get log of a custom model version dependency build.

        .. versionadded:: v2.22

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = self._log_path.format(self.custom_model_id, self.custom_model_version_id)
        return self._client.get(url).text

    def cancel(self):
        """Cancel custom model version dependency build that is in progress.

        .. versionadded:: v2.22

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = self._path.format(self.custom_model_id, self.custom_model_version_id)
        self._client.delete(url)

    def refresh(self):
        """Update custom model version dependency build with the latest data from server.

        .. versionadded:: v2.22

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = self._path.format(self.custom_model_id, self.custom_model_version_id)

        response = self._client.get(url)

        data = response.json()
        updated_data = self._update_server_data(
            data, self.custom_model_id, self.custom_model_version_id
        )
        self._set_values(**self._safe_data(updated_data, do_recursive=True))


class CustomDependencyConstraint(APIObject):
    """Metadata about a constraint on a dependency of a custom model version

    .. versionadded:: v2.22

    Attributes
    ----------
    constraint_type: str
        How the dependency should be constrained by version (<, <=, ==, >=, >)
    version: str
        The version to use in the dependency's constraint
    """

    _converter = t.Dict(
        {t.Key("constraint_type"): String(), t.Key("version"): String()}
    ).ignore_extra("*")

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return "{}(constraint_type={!r}, version={!r})".format(
            self.__class__.__name__,
            self.constraint_type,
            self.version,
        )

    def _set_values(self, constraint_type, version):
        self.constraint_type = constraint_type
        self.version = version


class CustomDependency(APIObject):
    """Metadata about an individual dependency of a custom model version

    .. versionadded:: v2.22

    Attributes
    ----------
    package_name: str
        The dependency's package name
    constraints: List[CustomDependencyConstraint]
        Version constraints to apply on the dependency
    line: str
        The original line from the requirements file
    line_number: int
        The line number the requirement was on in the requirements file
    """

    _converter = t.Dict(
        {
            t.Key("package_name"): String(),
            t.Key("constraints"): t.List(CustomDependencyConstraint.schema),
            t.Key("line"): String(),
            t.Key("line_number"): Int(gt=0),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return "{}(package_name={!r}, constraints={!r})".format(
            self.__class__.__name__,
            self.package_name,
            self.constraints,
        )

    def _set_values(self, package_name, constraints, line, line_number):
        self.package_name = package_name
        self.constraints = [CustomDependencyConstraint(**c) for c in constraints]
        self.line = line
        self.line_number = line_number


class CustomModelVersion(APIObject):
    """A version of a DataRobot custom model.

    .. versionadded:: v2.21

    Attributes
    ----------
    id: str
        id of the custom model version
    custom_model_id: str
        id of the custom model
    version_minor: int
        a minor version number of custom model version
    version_major: int
        a major version number of custom model version
    is_frozen: bool
        a flag if the custom model version is frozen
    items: List[CustomModelFileItem]
        a list of file items attached to the custom model version
    base_environment_id: str
        id of the environment to use with the model
    base_environment_version_id: str
        id of the environment version to use with the model
    label: str, optional
        short human readable string to label the version
    description: str, optional
        custom model version description
    created_at: str, optional
        ISO-8601 formatted timestamp of when the version was created
    dependencies: List[CustomDependency]
        the parsed dependencies of the custom model version if the
        version has a valid requirements.txt file
    network_egress_policy: datarobot.NETWORK_EGRESS_POLICY, optional
        Determines whether the given custom model is isolated, or can access the public network.
        Can be either 'datarobot.NONE' or 'datarobot.PUBLIC'
    maximum_memory: int, optional
        The maximum memory that might be allocated by the custom-model.
        If exceeded, the custom-model will be killed by k8s
    replicas: int, optional
        A fixed number of replicas that will be deployed in the cluster
    required_metadata_values: List[RequiredMetadataValue]
        Additional parameters required by the execution environment. The required keys are
        defined by the fieldNames in the base environment's requiredMetadataKeys.
    """

    _path = "customModels/{}/versions/"

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("custom_model_id"): String(),
            t.Key("version_minor"): Int(),
            t.Key("version_major"): Int(),
            t.Key("is_frozen"): t.Bool(),
            t.Key("items"): t.List(CustomModelFileItem.schema),
            # base_environment_id will be required once dependency management is enabled by default
            # in 6.2, but for backwards compatibility, this should be optional
            t.Key("base_environment_id", optional=True): String(),
            t.Key("base_environment_version_id", optional=True): String(),
            t.Key("label", optional=True): String(max_length=50, allow_blank=True) | t.Null(),
            t.Key("description", optional=True): String(max_length=10000, allow_blank=True)
            | t.Null(),
            t.Key("created", optional=True) >> "created_at": String(),
            t.Key("dependencies", optional=True): t.List(CustomDependency.schema),
            t.Key("network_egress_policy", optional=True): t.Enum(*NETWORK_EGRESS_POLICY.ALL),
            t.Key("maximum_memory", optional=True): Int(),
            t.Key("replicas", optional=True): Int(),
            t.Key("required_metadata_values", optional=True): t.List(RequiredMetadataValue.schema),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.label or self.id!r})"

    def _set_values(  # pylint: disable=missing-function-docstring
        self,
        id,
        custom_model_id,
        version_minor,
        version_major,
        is_frozen,
        items,
        base_environment_id=None,
        base_environment_version_id=None,
        label=None,
        description=None,
        created_at=None,
        dependencies=None,
        network_egress_policy=None,
        maximum_memory=None,
        replicas=None,
        required_metadata_values=None,
    ):
        self.id = id
        self.custom_model_id = custom_model_id
        self.version_minor = version_minor
        self.version_major = version_major
        self.is_frozen = is_frozen
        self.items = [CustomModelFileItem(**item) for item in items]
        self.base_environment_id = base_environment_id
        self.base_environment_version_id = base_environment_version_id
        self.label = label
        self.description = description
        self.created_at = created_at
        self.dependencies = [CustomDependency(**dep) for dep in dependencies or []]
        self.network_egress_policy = network_egress_policy
        self.maximum_memory = maximum_memory
        self.replicas = replicas
        self.required_metadata_values = (
            [RequiredMetadataValue.from_server_data(val) for val in required_metadata_values]
            if required_metadata_values
            else None
        )

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        initial = super().from_server_data(data, keep_attrs)
        # from_server_data will make the keys in requiredMetadata lowercase,
        # which is not OK. we need to preserve case
        initial.required_metadata = data.get("requiredMetadata")
        return initial

    @classmethod
    def create_clean(
        cls,
        custom_model_id,
        base_environment_id,
        is_major_update=True,
        folder_path=None,
        files=None,
        network_egress_policy=None,
        maximum_memory=None,
        replicas=None,
        required_metadata_values=None,
    ):
        """Create a custom model version without files from previous versions.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model
        base_environment_id: str
            the id of the base environment to use with the custom model version
        is_major_update: bool
            the flag defining if a custom model version
            will be a minor or a major version.
            Default to `True`
        folder_path: str, optional
            the path to a folder containing files to be uploaded.
            Each file in the folder is uploaded under path relative
            to a folder path
        files: list, optional
            the list of tuples, where values in each tuple are the local filesystem path and
            the path the file should be placed in the model.
            if list is of strings, then basenames will be used for tuples
            Example:
            [("/home/user/Documents/myModel/file1.txt", "file1.txt"),
            ("/home/user/Documents/myModel/folder/file2.txt", "folder/file2.txt")]
            or
            ["/home/user/Documents/myModel/file1.txt",
            "/home/user/Documents/myModel/folder/file2.txt"]
        network_egress_policy: datarobot.NETWORK_EGRESS_POLICY, optional
            Determines whether the given custom model is isolated, or can access the public network.
            Can be either 'datarobot.NONE' or 'datarobot.PUBLIC'
        maximum_memory: int, optional
            The maximum memory that might be allocated by the custom-model.
            If exceeded, the custom-model will be killed by k8s
        replicas: int, optional
            A fixed number of replicas that will be deployed in the cluster
        required_metadata_values: List[RequiredMetadataValue]
            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys.

        Returns
        -------
        CustomModelVersion
            created custom model version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        if files and not isinstance(files[0], tuple) and isinstance(files[0], str):
            files = [(filename, os.path.basename(filename)) for filename in files]
        return cls._create(
            "post",
            custom_model_id,
            is_major_update,
            base_environment_id,
            folder_path,
            files,
            network_egress_policy=network_egress_policy,
            maximum_memory=maximum_memory,
            replicas=replicas,
            required_metadata_values=required_metadata_values,
        )

    @classmethod
    def create_from_previous(
        cls,
        custom_model_id,
        base_environment_id,
        is_major_update=True,
        folder_path=None,
        files=None,
        files_to_delete=None,
        network_egress_policy=None,
        maximum_memory=None,
        replicas=None,
        required_metadata_values=None,
    ):
        """Create a custom model version containing files from a previous version.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model
        base_environment_id: str
            the id of the base environment to use with the custom model version
        is_major_update: bool, optional
            the flag defining if a custom model version
            will be a minor or a major version.
            Default to `True`
        folder_path: str, optional
            the path to a folder containing files to be uploaded.
            Each file in the folder is uploaded under path relative
            to a folder path
        files: list, optional
            the list of tuples, where values in each tuple are the local filesystem path and
            the path the file should be placed in the model.
            if list is of strings, then basenames will be used for tuples
            Example:
            [("/home/user/Documents/myModel/file1.txt", "file1.txt"),
            ("/home/user/Documents/myModel/folder/file2.txt", "folder/file2.txt")]
            or
            ["/home/user/Documents/myModel/file1.txt",
            "/home/user/Documents/myModel/folder/file2.txt"]
        files_to_delete: list, optional
            the list of a file items ids to be deleted
            Example: ["5ea95f7a4024030aba48e4f9", "5ea6b5da402403181895cc51"]
        network_egress_policy: datarobot.NETWORK_EGRESS_POLICY, optional
            Determines whether the given custom model is isolated, or can access the public network.
            Can be either 'datarobot.NONE' or 'datarobot.PUBLIC'
        maximum_memory: int, optional
            The maximum memory that might be allocated by the custom-model.
            If exceeded, the custom-model will be killed by k8s
        replicas: int, optional
            A fixed number of replicas that will be deployed in the cluster
        required_metadata_values: List[RequiredMetadataValue]
            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys.

        Returns
        -------
        CustomModelVersion
            created custom model version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        if files and not isinstance(files[0], tuple) and isinstance(files[0], str):
            files = [(filename, os.path.basename(filename)) for filename in files]
        if files_to_delete:
            upload_data = [("filesToDelete", file_id) for file_id in files_to_delete]
        else:
            upload_data = None
        return cls._create(
            "patch",
            custom_model_id,
            is_major_update,
            base_environment_id,
            folder_path,
            files,
            upload_data,
            network_egress_policy,
            maximum_memory,
            replicas,
            required_metadata_values=required_metadata_values,
        )

    @classmethod
    def _create(  # pylint: disable=missing-function-docstring
        cls,
        method,
        custom_model_id,
        is_major_update,
        base_environment_id,
        folder_path=None,
        files=None,
        extra_upload_data=None,
        network_egress_policy=None,
        maximum_memory=None,
        replicas=None,
        required_metadata_values=None,
    ):
        url = cls._path.format(custom_model_id)

        with contextlib2.ExitStack() as stack:
            upload_data = [
                ("isMajorUpdate", str(is_major_update)),
                ("baseEnvironmentId", base_environment_id),
            ]

            if folder_path:
                for root_path, _, file_paths in os.walk(folder_path):
                    for path in file_paths:
                        file_path = os.path.join(root_path, path)
                        file = stack.enter_context(
                            open(file_path, "rb")  # pylint: disable=consider-using-with
                        )

                        upload_data.append(("file", (os.path.basename(file_path), file)))
                        upload_data.append(("filePath", os.path.relpath(file_path, folder_path)))

            if files:
                for file_path, upload_file_path in files:
                    file = stack.enter_context(
                        open(file_path, "rb")  # pylint: disable=consider-using-with
                    )

                    upload_data.append(("file", (os.path.basename(upload_file_path), file)))
                    upload_data.append(("filePath", upload_file_path))

            if extra_upload_data:
                upload_data += extra_upload_data

            if network_egress_policy:
                upload_data.append(("networkEgressPolicy", network_egress_policy))

            if maximum_memory:
                upload_data.append(("maximumMemory", str(maximum_memory)))

            if replicas:
                upload_data.append(("replicas", str(replicas)))

            if required_metadata_values is not None:
                upload_data.append(
                    (
                        "requiredMetadataValues",
                        json.dumps(
                            [
                                {camelize(k): v for k, v in val.to_dict().items()}
                                for val in required_metadata_values
                            ]
                        ),
                    )
                )

            encoder = MultipartEncoder(fields=upload_data)
            headers = {"Content-Type": encoder.content_type}
            response = cls._client.request(method, url, data=encoder, headers=headers)
            return cls.from_server_data(response.json())

    @classmethod
    def list(cls, custom_model_id):
        """List custom model versions.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model

        Returns
        -------
        List[CustomModelVersion]
            a list of custom model versions

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = cls._path.format(custom_model_id)
        data = unpaginate(url, None, cls._client)
        return [cls.from_server_data(item) for item in data]

    @classmethod
    def get(cls, custom_model_id, custom_model_version_id):
        """Get custom model version by id.

        .. versionadded:: v2.21

        Parameters
        ----------
        custom_model_id: str
            the id of the custom model
        custom_model_version_id: str
            the id of the custom model version to retrieve

        Returns
        -------
        CustomModelVersion
            retrieved custom model version

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        url = cls._path.format(custom_model_id)
        path = f"{url}{custom_model_version_id}/"
        return cls.from_location(path)

    def download(self, file_path):
        """Download custom model version.

        .. versionadded:: v2.21

        Parameters
        ----------
        file_path: str
            path to create a file with custom model version content

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        url = self._path.format(self.custom_model_id)
        path = f"{url}{self.id}/download/"

        response = self._client.get(path)
        with open(file_path, "wb") as f:
            f.write(response.content)

    def update(self, description=None, required_metadata_values=None):
        """Update custom model version properties.

        .. versionadded:: v2.21

        Parameters
        ----------
        description: str
            new custom model version description
        required_metadata_values: List[RequiredMetadataValue]
            Additional parameters required by the execution environment. The required keys are
            defined by the fieldNames in the base environment's requiredMetadataKeys.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        payload = {}
        if description:
            payload.update({"description": description})

        if required_metadata_values is not None:
            payload.update(
                {"requiredMetadataValues": [val.to_dict() for val in required_metadata_values]}
            )

        url = self._path.format(self.custom_model_id)
        path = f"{url}{self.id}/"

        response = self._client.patch(path, data=payload)

        data = response.json()
        self._set_values(**self._safe_data(data, do_recursive=True))
        # _safe_data will make the keys in requiredMetadata lowercase,
        # which is not OK. we need to preserve case
        self.required_metadata = data.get(  # pylint: disable=attribute-defined-outside-init
            "requiredMetadata"
        )

    def refresh(self):
        """Update custom model version with the latest data from server.

        .. versionadded:: v2.21

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = self._path.format(self.custom_model_id)
        path = f"{url}{self.id}/"

        response = self._client.get(path)

        data = response.json()
        self._set_values(**self._safe_data(data, do_recursive=True))

    def get_feature_impact(self, with_metadata=False):
        """Get custom model feature impact.

        .. versionadded:: v2.23

        Parameters
        ----------
        with_metadata : bool
            The flag indicating if the result should include the metadata as well.

        Returns
        -------
        feature_impacts : list of dict
           The feature impact data. Each item is a dict with the keys 'featureName',
           'impactNormalized', and 'impactUnnormalized', and 'redundantWith'.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """
        url = self._path.format(self.custom_model_id)
        path = f"{url}{self.id}/featureImpact/"
        data = self._client.get(path).json()
        data = feature_impact_trafaret.check(data)
        return filter_feature_impact_result(data, with_metadata=with_metadata)

    def calculate_feature_impact(self, max_wait=DEFAULT_MAX_WAIT):
        """Calculate custom model feature impact.

        .. versionadded:: v2.23

        Parameters
        ----------
        max_wait: int, optional
            max time to wait for feature impact calculation.
            If set to None - method will return without waiting.
            Defaults to 10 min

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = self._path.format(self.custom_model_id)
        path = f"{url}{self.id}/featureImpact/"
        response = self._client.post(path)

        if max_wait is not None:
            wait_for_async_resolution(self._client, response.headers["Location"], max_wait)


class CustomModelVersionConversion(APIObject):
    """A conversion of a DataRobot custom model version.

    .. versionadded:: v2.27

    Attributes
    ----------
    id: str
        ID of the custom model version conversion.
    custom_model_version_id: str
        ID of the custom model version.
    created: str
        ISO-8601 timestamp of when the custom model conversion created.
    main_program_item_id: str or None
        ID of the main program item.
    log_message: str or None
        The conversion output log message.
    generated_metadata: dict or None
        The dict contains two items: 'outputDataset' & 'outputColumns'.
    conversion_succeeded: bool
        Whether the conversion succeeded or not.
    conversion_in_progress: bool
        Whether a given conversion is in progress or not.
    should_stop: bool
        Whether the user asked to stop a conversion.
    """

    _path = "customModels/{}/versions/{}/conversions/"

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("custom_model_version_id"): String(),
            t.Key("created"): String(),
            t.Key("main_program_item_id", optional=True): String(),
            t.Key("log_message", optional=True): String() | t.Null(),
            t.Key("generated_metadata", optional=True): t.Dict(
                {
                    t.Key("output_datasets"): t.List(t.String, min_length=0, max_length=50),
                    t.Key("output_columns"): t.List(
                        t.List(t.String, min_length=0, max_length=1024), min_length=1, max_length=50
                    ),
                }
            ),
            t.Key("conversion_succeeded", optional=True): t.Bool() | t.Null(),
            t.Key("conversion_in_progress", optional=True): t.Bool() | t.Null(),
            t.Key("should_stop", optional=True): t.Bool(),
        }
    ).ignore_extra("*")

    schema = _converter

    def __init__(self, **kwargs):
        self._set_values(**kwargs)
        self.custom_model_id = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id!r})"

    def _set_values(  # pylint: disable=missing-function-docstring
        self,
        id,
        custom_model_version_id,
        created,
        main_program_item_id=None,
        log_message=None,
        generated_metadata=None,
        conversion_succeeded=None,
        conversion_in_progress=None,
        should_stop=None,
    ):
        self.id = id
        self.custom_model_version_id = custom_model_version_id
        self.created = created
        self.main_program_item_id = main_program_item_id
        self.log_message = log_message
        self.generated_metadata = generated_metadata
        self.conversion_succeeded = conversion_succeeded
        self.conversion_in_progress = conversion_in_progress
        self.should_stop = should_stop

    @classmethod
    def run_conversion(
        cls,
        custom_model_id,
        custom_model_version_id,
        main_program_item_id,
        max_wait=None,
    ):
        """Initiate a new custom model version conversion.

        Parameters
        ----------
        custom_model_id : str
            The associated custom model ID.
        custom_model_version_id : str
            The associated custom model version ID.
        main_program_item_id : str
            The selected main program item ID. This should be one of the SAS items in the
            associated custom model version.
        max_wait: int or None
            Max wait time in seconds. If None, than don't wait.

        Returns
        -------
        conversion_id : str
            The ID of the newly created conversion entity.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx statuscustom model conversion
        """

        base_conversion_url = cls._path.format(custom_model_id, custom_model_version_id)
        payload = {"mainProgramItemId": main_program_item_id}
        response = cls._client.post(base_conversion_url, json=payload)
        if max_wait is not None:
            wait_for_async_resolution(cls._client, response.headers["Location"], max_wait)
        return response.json()["conversionId"]

    @classmethod
    def stop_conversion(cls, custom_model_id, custom_model_version_id, conversion_id):
        """
        Stop a conversion that is in progress.

        Parameters
        ----------
        custom_model_id : str
            ID of the associated custom model.
        custom_model_version_id : str
            ID of the associated custom model version.
        conversion_id :
            ID of a conversion that is in-progress.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """

        conversion = cls.get(custom_model_id, custom_model_version_id, conversion_id)
        if not conversion.conversion_in_progress:
            raise InvalidUsageError("You may only stop a conversion that is in progress.")

        base_conversion_url = cls._path.format(custom_model_id, custom_model_version_id)
        conversion_entity_url = "{}{}/".format(base_conversion_url, conversion_id)
        return cls._client.delete(conversion_entity_url)

    @classmethod
    def get(cls, custom_model_id, custom_model_version_id, conversion_id):
        """Get custom model version conversion by id.

        .. versionadded:: v2.27

        Parameters
        ----------
        custom_model_id: str
            The ID of the custom model.
        custom_model_version_id: str
            The ID of the custom model version.
        conversion_id: str
            The ID of the conversion to retrieve.

        Returns
        -------
        CustomModelVersionConversion
            Retrieved custom model version conversion.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """

        base_conversion_url = cls._path.format(custom_model_id, custom_model_version_id)
        conversion_entity_url = "{}{}/".format(base_conversion_url, conversion_id)
        return cls.from_location(conversion_entity_url)

    @classmethod
    def get_latest(cls, custom_model_id, custom_model_version_id):
        """Get latest custom model version conversion for a given custom model version.

        .. versionadded:: v2.27

        Parameters
        ----------
        custom_model_id: str
            The ID of the custom model.
        custom_model_version_id: str
            The ID of the custom model version.

        Returns
        -------
        CustomModelVersionConversion or None
            Retrieved latest conversion for a given custom model version.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """

        base_conversion_url = cls._path.format(custom_model_id, custom_model_version_id)
        data = unpaginate(base_conversion_url, {"isLatest": True}, cls._client)
        return cls.from_server_data(next(data))

    @classmethod
    def list(cls, custom_model_id, custom_model_version_id):
        """Get custom model version conversions list per custom model version.

        .. versionadded:: v2.27

        Parameters
        ----------
        custom_model_id: str
            The ID of the custom model.
        custom_model_version_id: str
            The ID of the custom model version.

        Returns
        -------
        List[CustomModelVersionConversion]
            Retrieved conversions for a given custom model version.

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status.
        datarobot.errors.ServerError
            if the server responded with 5xx status.
        """

        base_conversion_url = cls._path.format(custom_model_id, custom_model_version_id)
        data = unpaginate(base_conversion_url, None, cls._client)
        return [cls.from_server_data(item) for item in data]
