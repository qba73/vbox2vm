import pytest
from ovf.ovf import readovf
from ovf.ovf import Ovf


@pytest.fixture(scope="session")
def soup():
    test_file = "tests/centos7-packer-tmpl.ovf"
    s = readovf(test_file)
    return s


def test_references_should_return_reference_file_name(soup):
    ovf = Ovf(soup)
    res = ovf.references()
    assert res['file_href'] == "centos7-packer-tmpl-disk1.vmdk"


def test_references_should_return_reference_file_id(soup):
    ovf = Ovf(soup)
    res = ovf.references()
    assert res['file_id'] == "file1"


@pytest.mark.parametrize("disk_param, expected", [
    ("ovf_disk_capacity", "8388608000" ),
    ("ovf_disk_diskid", "vmdisk1"),
    ("ovf_disk_fileref", "file1"),
    ("ovf_disk_format", "http://www.vmware.com/interfaces/specifications/vmdk.html#streamOptimized"),
    ("vbox_disk_uuid", "539c2169-1bdd-4e83-b3e9-b651469014d8")
])
def test_disk_should_return_disk_info(soup, disk_param, expected):
    ovf = Ovf(soup)
    res = ovf.disk()
    assert res[disk_param] == expected


def test_network_should_return_network_name(soup):
    ovf = Ovf(soup)
    res = ovf.network()
    assert res['ovf_network_name'] == 'NAT'


@pytest.mark.parametrize("vsparam, expected", [
    ("virtual_system_id", "centos7-packer-tmpl"),
    ("virtual_system_identifier", "centos7-packer-tmpl"),
    ("virtual_system_type", "virtualbox-2.2")
])
def test_virtual_system_should_return_packer_system_name(soup, vsparam, expected):
    ovf = Ovf(soup)
    res = ovf.virtual_system()
    assert res[vsparam] == expected


@pytest.mark.parametrize("osparam, expected", [
    ("oss_id", "80"),
    ("oss_description", "RedHat_64"),
    ("oss_type", "RedHat_64")
])
def test_operating_system_should_return(soup, osparam, expected):
    ovf = Ovf(soup)
    res = ovf.operating_system()
    assert res[osparam] == expected


def test_context_should_return_dict(soup):
    ovf = Ovf(soup)
    assert isinstance(ovf.context, dict)


def test_context_contains_all_required_by_jinja_vars(soup):
    ovf = Ovf(soup)
    context = ovf.context
    jinja_items = ('file_href',
                   'file_id',
                   'ovf_disk_capacity',
                   'ovf_disk_diskid',
                   'ovf_disk_fileref',
                   'ovf_disk_format',
                   'vbox_disk_uuid',
                   'ovf_network_name',
                   'virtual_system_id',
                   'virtual_system_identifier',
                   'virtual_system_type',
                   'oss_id',
                   'oss_description',
                   'oss_type',
                   'cpus',
                   'memory')
    for item in jinja_items:
        assert item in context


def test_cpus_should_return_number_of_cpus(soup):
    ovf = Ovf(soup)
    assert ovf.cpus()['cpus'] == 1


def test_memory_should_return_memory_in_MB(soup):
    ovf = Ovf(soup)
    assert ovf.memory()['memory'] == 2048


def test_update_shoudl_update_given_context_params(soup):
    ovf = Ovf(soup)
    context = ovf.update(oss_id=80,
                         oss_description='CentOS',
                         oss_type='rhel7',
                         virtual_system_type='vmx-7')
    assert context['oss_id'] == 80
    assert context['oss_description'] == 'CentOS'
    assert context['oss_type'] == 'rhel7'
    assert context['virtual_system_type'] == 'vmx-7'
