#!/usr/bin/env python

import os
import click
from bs4 import BeautifulSoup as bs
from jinja2 import Environment, FileSystemLoader, Template

this_dir = os.path.dirname(os.path.abspath(__file__))

j2_env = Environment(loader=FileSystemLoader(this_dir + '/templates'),
                     trim_blocks=True)


class Ovf(object):
    def __init__(self, soup):
        self.soup = soup

    def _virtual_hardware_section(self):
        return self.soup.find('virtualhardwaresection')
        
    def _get_hardware_item(self, hardware):
        '''Return bs object for given hardware

        Args:
          hardware: str, one of 'CPU', 'MB'
        '''
        hs = self._virtual_hardware_section()
        item = [item for item in hs.find_all('item') if hardware in item.find('rasd:caption').text]
        return int(item[0].find('rasd:virtualquantity').text)

    def references(self):
        references = self.soup.find('references')
        file_href = references.find('file')['ovf:href']
        file_id = references.find('file')['ovf:id']
        context = {
            "file_href": file_href,
            "file_id": file_id
        }
        return context

    def disk(self):
        '''Return disk info (dict) parsed from DiskSection of the ovf file.'''
        disk_section = self.soup.find('disksection')
        disk = disk_section.find('disk')
        context = {
            "ovf_disk_capacity": disk['ovf:capacity'],
            "ovf_disk_diskid": disk['ovf:diskid'],
            "ovf_disk_fileref": disk['ovf:fileref'],
            "ovf_disk_format": disk['ovf:format'],
            "vbox_disk_uuid": disk['vbox:uuid']
        }
        return context

    def network(self):
        network_section = self.soup.find('networksection')
        network = network_section.find('network') 
        context = {
            "ovf_network_name": network['ovf:name']
        }
        return context

    def virtual_system(self):
        virt_system = self.soup.find('virtualsystem')
        hardware_section = virt_system.find('virtualhardwaresection')
        system = hardware_section.find('system')
        virt_system_type = system.find('vssd:virtualsystemtype').text
        context = {
            'virtual_system_id': virt_system['ovf:id'],
            'virtual_system_identifier': virt_system['ovf:id'],
            'virtual_system_type': virt_system_type
        }
        return context

    def operating_system(self):
        oss = self.soup.find('operatingsystemsection')
        description = oss.find('description').text
        os_type = oss.find('vbox:ostype').text
        context = {
             "oss_id": oss['ovf:id'],
             "oss_description": description,
             "oss_type": os_type
        }
        return context

    def cpus(self):
        cpus = self._get_hardware_item('CPU')
        context = {"cpus": cpus}
        return context

    def memory(self):
        mem = self._get_hardware_item('MB')
        context = {"memory": mem}
        return context

    @property
    def context(self):
        con = dict()
        for item in (self.references(),
                     self.disk(),
                     self.network(),
                     self.virtual_system(),
                     self.operating_system(),
                     self.cpus(),
                     self.memory()):
            con.update(item)
        return con

    def update(self, **kwargs):
        '''Return new context with updated params.'''
        new_context = {k:v for k,v in self.context.items()}
        new_context.update(kwargs)
        return new_context


def readovf(ovfin):
    with open(ovfin, 'r') as f:
        soup = bs(f, "lxml")
    return soup


def create_ovf_template(template_name, context):
    template = j2_env.get_template(template_name)
    return template.render(context)


def save_ovf(template, ovfout):
    with open(ovfout, "w") as fout:
        fout.write(template)


def make_context(ovfin, **kwargs):
    soup = readovf(ovfin)
    ovf = Ovf(soup)
    context = ovf.update(**kwargs)
    return context
     

@click.command()
@click.argument('ovfin')
@click.argument('ovfout')
@click.option('--template_name', default='centos7.ovf.j2',
              help="Ovf VMware template. Default: 'centos7.ovf.j2'")
@click.option('--oss_id', default=107,
              help='VMware code for RedHat family. Default: 107')
@click.option('--oss_description', default='CentOS 4/5/6/7 (64-bit)')
@click.option('--oss_type', default='rhel7_64Guest',
              help="VMware code for RedHat 64bit family. Default: 'rhel7_64Guest'")
@click.option('--virtual_system_type', default='vmx-10',
              help='VMware virtual system type. Default: vmx-10')
def cli(ovfin, ovfout, template_name, oss_id, oss_description, oss_type, virtual_system_type):
    click.echo("Reading ovf file")
    context = make_context(ovfin,
                           oss_id=oss_id,
                           oss_description=oss_description,
                           oss_type=oss_type,
                           virtual_system_type=virtual_system_type)
    click.echo("Generating OVF vSphere file with params:")
    click.echo("oss_id: {}, oss_description: {}, oss_type: {}, virtual_system_type: {}".format(
        oss_id, oss_description, oss_type, virtual_system_type))
    ovftmp = create_ovf_template(template_name, context=context)
    save_ovf(ovftmp, ovfout)
    click.echo("Saved updated ovf file: {}".format(ovfout))
