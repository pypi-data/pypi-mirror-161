resource "aws_route_table_association" "{{data.rname}}" {
{% if data.import_resources %}
  subnet_id      = {{data.subnet_id_ref}}
  route_table_id =  {{data.route_table_id_ref}}
{% else %}
  subnet_id      = "{{data.subnet_id}}"
  route_table_id = "{{data.route_table_id}}"
{% endif %}
  provider       = {{data.provider}}
}

