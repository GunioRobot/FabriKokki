from __future__ import with_statement

import os
import re
from kokki.base import Fail
from kokki.providers import Provider

class MountProvider(Provider):
    def action_mount(self):
        if not fabric.contrib.files.exists(self.resource.mount_point):
            fabric.sudo('mkdir -p ' + self.resource.mount_point)

        if self.is_mounted():
            self.log.debug("%s already mounted" % self)
        else:
            args = ["mount"]
            if self.resource.fstype:
                args += ["-t", self.resource.fstype]
            if self.resource.options:
                args += ["-o", ",".join(self.resource.options)]
            if self.resource.device:
                args.append(self.resource.device)
            args.append(self.resource.mount_point)

            fabric.sudo(args)

            self.log.info("%s mounted" % self)
            self.resource.updated()

    def action_umount(self):
        if self.is_mounted():
            fabric.sudo("umount " + self.resource.mount_point)

            self.log.info("%s unmounted" % self)
            self.resource.updated()
        else:
            self.log.debug("%s is not mounted" % self)

    #FIXME: make this work over the network
    #def action_enable(self):
    #    if self.is_enabled():
    #        self.log.debug("%s already enabled" % self)
    #    else:
    #        if not self.resource.device:
    #            raise Fail("[%s] device not set but required for enable action" % self)
    #        if not self.resource.fstype:
    #            raise Fail("[%s] fstype not set but required for enable action" % self)
    #
    #        with open("/etc/fstab", "a") as fp:
    #            fp.write("%s %s %s %s %d %d\n" % (
    #                    self.resource.device,
    #                    self.resource.mount_point,
    #                    self.resource.fstype,
    #                    ",".join(self.resource.options or ["defaults"]),
    #                    self.resource.dump,
    #                    self.resource.passno,
    #                ))
    #
    #        self.log.info("%s enabled" % self)
    #        self.resource.updated()

    def action_disasble(self):
        pass # TODO

    def is_mounted(self):
        if not fabric.contrib.files.exists(self.resource.mount_point):
            return False

        if self.resource.device and not fabric.contrib.files.exists(self.resource.device):
            raise Fail("%s Device %s does not exist" % (self, self.resource.device))

        mounts = self.get_mounted()
        for m in mounts:
            if m['mount_point'] == self.resource.mount_point:
                return True

        return False

    def is_enabled(self):
        mounts = self.get_fstab()
        for m in mounts:
            if m['mount_point'] == self.resource.mount_point:
                return True

        return False

    def get_mounted(self):
        out = fabric.sudo("mount")
        #if p.wait() != 0:
        #    raise Fail("[%s] Getting list of mounts (calling mount) failed" % self)

        mounts = [x.split(' ') for x in out.strip().split('\n')]

        return [dict(
                device = m[0],
                mount_point = m[2],
                fstype = m[4],
                options = m[5][1:-1].split(','),
            ) for m in mounts if m[1] == "on" and m[3] == "type"]
        
    #FIXME: make this work over the network
    #def get_fstab(self):
    #    mounts = []
    #    with open("/etc/fstab", "r") as fp:
    #        for line in fp:
    #            line = line.split('#', 1)[0].strip()
    #            mount = re.split('\s+', line)
    #            if len(mount) == 6:
    #                mounts.append(dict(
    #                    device = mount[0],
    #                    mount_point = mount[1],
    #                    fstype = mount[2],
    #                    options = mount[3].split(","),
    #                    dump = int(mount[4]),
    #                    passno = int(mount[5]),
    #                ))
    #    return mounts
