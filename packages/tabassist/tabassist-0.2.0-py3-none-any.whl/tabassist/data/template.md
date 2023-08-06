# {{ doc_name }}

## Описание дашборда
to be updated...

## Кто пользуется дашбордом 
to be updated...

## Частота обновления 
to be updated...

{% for ds in datasources  -%}
## {{ ds.caption }}

### Местонахождение

{% for conn in ds.connections  %}
Сервер - {{ conn.server }}  
Тип БД - {{ conn.dbclass }}  
База данных - {{ conn.dbname }}  
Порт - {{ conn.port }}  

{% endfor %}

### Описание полей

| Наименование | Описание | Формула |
| ------ | ------ | ------ |
{% for col in ds.fields -%}
{%- if ds.fields[col].calculation %}
    {{- ds.fields[col].caption}} | | {{ ds.fields[col].calculation.replace('\n', '<br/>').replace(' ', '&ensp;') }}
{% else %}
    {{- ds.fields[col].name.replace('[', '').replace(']', '') }} | | 
        {%- if ds.fields[col].calculation -%}
            {{ ds.fields[col].calculation.replace('\n', '<br/>').replace(' ', '&ensp;') }}
        {%- else -%}
            {{ ds.fields[col].calculation }}
        {%- endif %}
{% endif %}
{%- endfor %}
{%- endfor %}

## Known issues and workaround

not found yet.
