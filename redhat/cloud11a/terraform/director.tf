resource "libvirt_volume" "ieatrheldir11a_vol"{
  name = "ieatrheldir11a_vol"
  base_volume_id = libvirt_volume.rhel_7_7.id
  // 200GB image
  size = 214748364800
}
locals {
 ssh_pub_key = file("~/.ssh/id_rsa.pub")
}

# Use CloudInit to add our ssh-key to the instance
resource "libvirt_cloudinit_disk" "ieatrheldir11a_cloudinit_disk" {
  name = "ieatrheldir11a_cloudinit_disk"

  user_data = <<EOF
#cloud-config
debug: True
chpasswd:
  expire: False
  list: |
    root:$6$W6ORbdzbXRyoGi8q$ngK6XTeu7JljHXlTQxg1HiqsWSquy7TXu2Yeqax7kTyfKskmBzVZab///mAkWY37U65wDGauN3G71gH/SpaJx/
  
local-hostname: "ieatrheldir11a"
disable_root: 0
ssh_pwauth: 1
timezone: Europe/Dublin
locale: en_IE.utf8

users:
  - name: stack
    lock_passwd: False
    passwd: '$6$XtX2JYoGf0UbN9lb$Kb9EV.9kEjAADcPzrhiJEOvq5.USUuWgmkUhERj0zLMXVYafPosyIO3mRCo0Tvbx3w8PETgISgzatsK8sFqkI/'
    ssh_authorized_keys:
      - ${local.ssh_pub_key}

runcmd:
  - sed -i -e 's/^.*UseDNS.*/UseDNS no/g' /etc/ssh/sshd_config
  - systemctl restart sshd
  - systemctl disable NetworkManager
  - sed -i -e 's/.*10\.0.*//g' /etc/resolv.conf
  - localectl set-keymap ie

write_files:
  - content: |
      stack ALL=(root) NOPASSWD:ALL
      permissions: 0440
      owner: root:root
      path: /etc/sudoers.d/stack

growpart:
  mode: auto
  devices: ['/']
output: { all: "| tee -a /var/log/cloud-init-output.log" }

EOF
network_config = file("director_net_config")
meta_data = <<EOF
instance-id: "ieatrheldir11a-001"
local-hostname: "ieatrheldir11a"
EOF
}
resource "libvirt_domain" "ieatrheldir11a" {
  name = "ieatrheldir11a"
  memory = "32768"
  vcpu = 16
  network_interface {
    bridge= var.ext_bridge
   
  }
  network_interface {
    bridge= var.prov_bridge
 }
  network_interface {
    bridge = var.int_bridge
  }
  cloudinit = libvirt_cloudinit_disk.ieatrheldir11a_cloudinit_disk.id
  disk {
   volume_id = libvirt_volume.ieatrheldir11a_vol.id
   scsi = "true"
  }
  video {
    type = "vga"
  }
  graphics {
    type = "vnc"
    listen_type = "address"
 }
}

terraform {
  required_version = ">= 0.12"
}
