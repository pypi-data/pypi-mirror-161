[сlass]: # (блок класса)
# <p style="text-align: center">Argument parser</p>

--------------

     file: ArgParser.py
     class: ArgumentParser

<p>Класс для парсинга аргументов из командной строки.</p>
<br>

[methods]: # (блок методов)

## <p style="text-align: center">Методы</p>

--------------

#### <p style="text-align: center; font-weight: bolder">add_rule( )</p>

    ArgumentParse.add_rule(flag, var_name)
    
    ex: ArgumentParse.add_rule('-key', 'MyKey'),
        ArgumentParse.add_rule(['-key1', '-key2'], 'MyKey')

<div style="margin: 30px 0">
    <p><span style="color: green">var_name</span> - имя переменной, которая будет содержать значение после флага</p>
    <p><span style="color: green">flag</span> - флаг для обозначения аргумента (должен начинаться с "-" и стоять перед значением)</p>
</div>

--------------

#### <p style="text-align: center; font-weight: bolder">add_rules_dict( )</p>

    ArgumentParse.add_rules_dict(rules)
    
    ex: ArgumentParse.add_rules_dict({
        'key1': '-flag1',
        'key2': ['-flag2', '-flag3']
    })

<div style="margin: 30px 0">
    <p><span style="color: green">rules</span> - словарь с правилами { var_name: flags } </p>
</div>

--------------

#### <p style="text-align: center; font-weight: bolder">parse( )</p>

    ArgumentParse.parse(args_list = None)
    
    ex: ArgumentParse.parse()

<div style="margin: 30px 0">
    <p><span style="color: green">args_list</span> - список аргументов. Если None, то парсинг происходит из sys.argv </p>
</div>

--------------


[сlass]: # (блок класса)
# <p style="text-align: center">Argument list</p>

--------------

     file: ArgParser.py
     class: ArgumentList

<p>Класс, содержащий аргументы консоли после ArgumentParser.parse().</p>
<p>Singleton, следовательно каждый созданный экземпляр класса будет содержать, что и другие те же переменные.</p>
<br>

--------------

[usage]: # (блок применения)

## <p style="text-align: center">Применение</p>

--------------
    ex: python main.py --host smth.ru
<p>main.py:</p>

    from AEngine_console.ArgParser import ArgumentParser, ArgumentList
    
    ArgumentParser.add_rule('host', ['--host', '-h'])
    ArgumentParser.parse()
    args = ArgumentList()
    print(args.host)
<p></p>
    
    output: smth.ru
