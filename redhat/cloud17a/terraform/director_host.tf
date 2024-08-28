variable "director_host"{
}
variable "ext_bridge" {
}
variable "prov_bridge" {
}
variable "int_bridge" {
}

provider "libvirt" {
    uri = "qemu+ssh://root@${var.director_host}/system"
}
resource "libvirt_volume" "rhel_7_7"{
  name = "rhel-server-7.7-x86_64-kvm.qcow2"
  pool = "default"
  format = "qcow2"
}
