resource "azurerm_subnet_route_table_association" "$rname" {
  subnet_id      = $subnet_ref
  route_table_id = $route_table_ref
  provider       = azurerm.$provider
}
