#!/usr/bin/python
from oslo_log import log as logging
try:
    import rados
    import rbd
except ImportError:
    rados = None
    rbd = None

LOG = logging.getLogger(__name__)

#Khai bao ceph config
cluster = rados.Rados(conffile='/etc/ceph/ceph.conf')
cluster.connect()

#Khai bao ten pool(string)
ioctx = cluster.open_ioctx('vms-hdd')

#Khai bao ten image(string)
name = "e9c58ed1-3b37-4a65-a66c-7bc44d12a04f_disk"

rbd_inst = rbd.RBD()

extents = []
extents_snap = []

#Khai bao ten snapshot (String)
snapshot = str

rbd_img = rbd.Image(ioctx, name, snapshot=None, read_only=False)
def iterate_cb(offset, length, exists):
    if exists:
        extents.append(length)

rbd_img.diff_iterate(0, rbd_img.size(), None, iterate_cb, include_parent=True, whole_object=False)

def iterate_cb_snap(offset, length, exists):
    if exists:
        extents_snap.append(length)

rbd_img.diff_iterate(0, rbd_img.size(), snapshot, iterate_cb_snap, include_parent=True, whole_object=False)

if extents:
    extents_from_0 = int(sum(extents))
    LOG.debug("RBD has %s extents", extents_from_0)


if extents_snap:
    extents_from_snap = int(sum(extents_snap))
    LOG.debug("RBD has %s extents from snapshot", extents_from_snap)

snap_size = extents_from_0 - extents_from_snap