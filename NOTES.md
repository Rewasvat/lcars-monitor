# LCARS Monitor

## Estrutura da HardwareMonitor LIB
- [Computer]:
    - tem uns dados de bios e tal do PC
    - nome do PC?
    - Lista de N [Hardware]

- [Hardware] (HW):
    - tem ID / Name / HardwareType
    - tem Properties, altho não aparentam ser uteis? <tem que testar!>
    - Lista de N sub-[Hardware]
    - Lista de N [Sensor]

- [Sensor]:
    - Tem ID / Index (no HW pai) / Name / SensorType
    - SensorType determina tipo do sensor, e portanto a unidade dos valores
    - Tem Value / Min / Max.
        - tb tem Values: uma lista de Value + Timestamp. Serve pra Plots?
    - Tem lista de Parameters, mas esses o Report indica que não servem pra muita coisa

## Estrutura do LCARS Monitor

- App:
    - Minha Idéia:
        - Janela com 2 regioes: escolha de tab, e "area principal"
        - Tabs possíveis:
            - Dashboard
                - deve ser configurável pelo App
                    - Salva em JSON (junto com o EXE)
                    - poder editar a config pelo app
                - Mostra [Widget]s configurados
                - distribui widgets pela ordem de acordo com tamanho disponivel
            - Uma tab pra cada tipo de HW (CPU, GPU, Motherboard, etc)
    - Idéia do Fábio
        - clone do AIDA64 Ex basicamente
        - tem 2 janelas:
            - Janela do App:
                - Serve pra configurar tamanho, widgets e etc do "monitor"
            - Janela do Monitor
                - Janela separada, possivelmente com tamanho fixo, pra mostrar os widgets configurados
        - Nesse caso, considerando o acima, seria mais facil fazer 2 apps:
            - um app "editor", que mostra esse esquema de 2 janelas, uma de configurar coisas e outra de "monitor"
            - outro app que só mostra puramente a janela do monitor, que deve ter sido previamente configurada
        - talvez daria pra configurar um unico app que mostra na system-tray, e mostra a janela do monitor.
            - ai pelo monitor não configurado, ou pela tray, é possivel abrir a janela do editor pra configurar as coisas.
            - um pouco mais complexo do que ter 2 apps separados, mas probs ficaria melhor.

## Widget
- widget configurável pra posicionar no app/dashboard
- essa classe base seria só pros elementos puramente visuais (como imagens e texto)
- talvez ter outras classes derivadas dessa pra implementar os elementos visuais em si? como imagem, texto e tal

* note que a principio iriamos deixar o estilo visual fixo em LCARS
    - então escolher imagens fixas desse estilo, cores da paleta lcars, etc
    - ai as configurações de visual nesses widgets seriam simplificadas pra ser só dessas opções "lcars"
    - mas provavelmente iriamos querer alguns widgets "pre-feitos" pra simplicar certas coisas, como uma barra no estilo de "reator", etc

### SensorWidget (Widget)
- deriva de Widget, adicionando funcionalidade pra incorporar dados de um sensor
- associado a um HW/sensor
- mostra dados de algum jeito
    - sensor name e value (current/max/min/plot?)
    - custom label
- poder customizar
    - estilo/layout?
    - tipo do widget?
- talvez interaction pra:
    - mudar algo no widget
    - mudar o widget em si
    - mudar tab selecionada

### AverageSensorWidget (SensorWidget?) name-pending
- talvez deriva de SensorWidget?
- idéia seria um widget que está associado a N sensores, ou a um grupo de sensores (sensores tem que ser do mesmo tipo!)
- mostra alguma stat desse grupo de sensores, como média dos valores, etc

### Estrutura de classes / Arquitetura dos Widgets
- Widgets
    - ImageWidget
    - TextWidget
    - CompositeWidget?
        - em layouts posicionais absolutos (tipo ideia do fabio), isso nao seria necessario (exemplo: vc simplesmente coloca um TextWidget em cima do ImageWidget pra ter uma img+text)
        - em um layout automatico, como poderia ocorrer na minha ideia, algo assim seria necessario pra poder colocar um widget em cima do outro por exemplo
            - mas ai tb poderia ser algo tipo um "PanelWidget" q pode ser um elemento visual e ainda ter filhos-widgets
            - interface ficaria bem parecida com os Controls que usamos no WinForms :hmmm:
    - SensorWidget
    - AverageSensorWidget
    > isso teria problemas de associacao...
        > teria que implementar varias classes, umas derivadas de outras, talvez interfaces tb
        > meio que tá recriando código: pq uma classe de TextWidget se um Control Text/Label já é exatamente isso (talvez só mudando certas configs)?
        > ai se quisermos ter um "Sensor+TextWidget" ou "Sensor+ImageWidget", como fariamos... Seria melhor a conexão com os dados ser algo separado dessa arvore de classes.

- Widget (ideia #2)
    - um classe composta, contem:
        - um "visual": um WinForm Control
            - ou alguma outra subclasse que representa os controles de winForms, mas acho que é essa mesma
        - uma "fonte de dados": um sensor
            - ai pode ser um sensor de HW mesmo
            - e podemos ter um "Static Sensor":
                - implementamos um Sensor nosso que não faz nada, simplesmente retorna um dado valor com qual foi criado
                - assim a API da widget pode só receber Sensor (ou ISensor), mas podemos ter os widgets "estaticos" de puro texto/imagem ou whatever sem ter dados de algum sensor real.
        - uma "ponte": um implementação especifica de IVisitor pra sensor, que pega os dados do sensor associado e atualiza o controle associado com tais dados
            - dai a "implementação especifica": probs teremos que ter varias implementações diferentes de Visitors, pra cada tipo de Control aceito
                - isso meio que serve como limitante de quais controles são aceitos.
                - poderia servir como um "inicializador nosso" do Controle tb, pra setar certas propriedades (alem do update dos dados).
                    - Assim widget não precisaria de código especifico pra certos Controles pra setar certas propriedades
                    - coisas como deixar um botão desabilitado
                - se pá é melhor esse objeto CONTER o Controle adequado - criar, e guardar ele. Assim o Widget não se preocupa com isso, soh recebe Sensor/Visitor
        - uma config, isso pode incluir:
            - dados de como inicializar/customizar o Control
            - especificacao da Fonte de Dados, como pegar/criar ela
            - config do Visitor/Ponte, que pode ter coisa de como mudar comportamento dele, talvez até coisas do control tb
    > essa ideia parece uma arquitetura melhor
        > nao fica limitado com as particularidades de herança de classes e interfaces

- class Widget (a #2)
- class StaticSensor (implementa ISensor) ?
- class WidgetVisitor (WV, implementa IVisitor)
    - classe base de Visitors pros Widgets
    - pode cuidar do Controle "associado": cria/guarda ele (altho isso é mais caso pros filhos)
    - talvez ter utils das unidades dos sensores?
- folder Visitors
    - class LabelVisitor (extende WidgetVisitor): cria e faz o update de uma Label com dados do sensor
    - visitors pra outros controles?
- class WidgetSystem:
    - lista widgets existentes
    - salva/carrega config dos widgets
- talvez alguma classe pra abstrair a Config do Widget?
    - é capaz de ter alguns dados padrões (tipo ID/etc do Sensor associado, e qual classe de WV tá usando)
    - mas resto dos dados será especifico da class de WV
    - entao alguma forma de Widget/WV definirem/load/save os dados "comuns", enquanto API do WV que classe implementa define/load/save seus dados especificos seria melhor
    - de preferencia salvar dados as JSON, mas se não rolar pesquisar alguma forma de serialização binária estilo python-pickle... C# acho que tem algo assim tb