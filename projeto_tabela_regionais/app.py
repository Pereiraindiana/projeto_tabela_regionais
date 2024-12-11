
import pandas as pd

# Carregar o arquivo Excel
excel_file = "data/seu_arquivo.xlsx"
df = pd.read_excel(excel_file, engine='openpyxl')

# Exibir o DataFrame para conferir
print(df.head())

# Converter para HTML
html_table = df.to_html(index=False)

# HTML com Estilo e Funcionalidades de Filtro, Ordenação e Paginação
html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tabela de Regionais Atendidas</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f9;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }}
        table {{
            width: 80%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        input[type="text"] {{
            width: 100%;
            padding: 8px;
            margin: 10px 0;
            border-radius: 5px;
            border: 1px solid #ccc;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
    <script>
        $(document).ready(function() {{
            // Filtragem da tabela
            $('#filter').on('input', function() {{
                var value = $(this).val().toLowerCase();
                $('#dataTable tr').filter(function() {{
                    $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1);
                }});
            }});

            // Ordenação da tabela
            $('th').click(function() {{
                var table = $(this).parents('table');
                var rows = table.find('tr:gt(0)').toArray().sort(compare($(this).index()));
                this.asc = !this.asc;
                if (!this.asc) rows = rows.reverse();
                table.append(rows);
            }});
            
            function compare(index) {{
                return function(a, b) {{
                    var A = getCellValue(a, index), B = getCellValue(b, index);
                    return $.isNumeric(A) && $.isNumeric(B) ? A - B : A.localeCompare(B);
                }};
            }}
            
            function getCellValue(row, index) {{
                return $(row).children('td').eq(index).text();
            }}
        }});
    </script>
</head>
<body>
    <h1>Regionais Atendidas</h1>

    <input type="text" id="filter" placeholder="Filtrar por qualquer dado...">

    <table id="dataTable">
        <thead>
            <tr>
                <th>Numero da Loja</th>
                <th>Nome da Loja</th>
                <th>Região</th>
                <th>Parceiro de Entrega</th>
                <th>Caixa Atendido (PDV)</th>
            </tr>
        </thead>
        <tbody>
            {html_table.split('<thead>')[1].split('</thead>')[1]}
        </tbody>
    </table>

</body>
</html>
"""

# Salvar a página HTML
with open('templates/tabela_atendida_com_filtros.html', 'w') as f:
    f.write(html_content)

print("HTML gerado com sucesso!")
        