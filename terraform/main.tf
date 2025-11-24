provider "azurerm" {
  features {}
  subscription_id = "ba06c474-bc95-47af-99a1-fd77201246f7"
}


data "azurerm_resource_group" "rg" {
  name = "ansible-rg"
}


data "azurerm_network_interface" "vm1_nic" {
  name                = "manage-node1355_z1"
  resource_group_name = data.azurerm_resource_group.rg.name
}

data "azurerm_network_interface" "vm2_nic" {
  name                = "manage-node2391_z1"
  resource_group_name = data.azurerm_resource_group.rg.name
}


locals {
  vm1_pub_id_parts = split("/", data.azurerm_network_interface.vm1_nic.ip_configuration[0].public_ip_address_id != "" ?>
  vm2_pub_id_parts = split("/", data.azurerm_network_interface.vm2_nic.ip_configuration[0].public_ip_address_id != "" ?>

  vm1_pub_name = length(local.vm1_pub_id_parts) > 0 ? element(local.vm1_pub_id_parts, length(local.vm1_pub_id_parts) - >
  vm2_pub_name = length(local.vm2_pub_id_parts) > 0 ? element(local.vm2_pub_id_parts, length(local.vm2_pub_id_parts) - >

  vm1_pub_rg = length(local.vm1_pub_id_parts) > 4 ? element(local.vm1_pub_id_parts, 4) : ""
  vm2_pub_rg = length(local.vm2_pub_id_parts) > 4 ? element(local.vm2_pub_id_parts, 4) : ""
}


data "azurerm_public_ip" "vm1_pub" {
  count                = local.vm1_pub_name != "" ? 1 : 0
  name                 = local.vm1_pub_name
  resource_group_name  = local.vm1_pub_rg
}

data "azurerm_public_ip" "vm2_pub" {
  count                = local.vm2_pub_name != "" ? 1 : 0
  name                 = local.vm2_pub_name
  resource_group_name  = local.vm2_pub_rg
}
