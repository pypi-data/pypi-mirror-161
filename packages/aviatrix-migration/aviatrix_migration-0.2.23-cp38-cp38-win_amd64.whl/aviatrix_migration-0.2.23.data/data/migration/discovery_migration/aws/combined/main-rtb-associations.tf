resource "aws_main_route_table_association" "{{data.rname}}" {
  vpc_id         = "{{data.vpc_id}}"
{% if data.import_resources %}
  route_table_id = {{data.route_table_id_ref}}
{% else %}
  route_table_id = "{{data.route_table_id}}"
{% endif %}
  provider       = {{data.provider}}
}

