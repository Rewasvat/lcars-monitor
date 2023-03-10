TODO

# PASSAR TODOS PRA ISSUES NO GITHUB ???

# DOCUMENTAR CLASSES E METODOS!

# STUFF
- [WidgetVisitor]:
    + suport a unidades dos sensores
    + suport a formatacao padrao dos valores dos sensores
    - verificar se o valor de um sensor tá no range critico (ICriticalSensorLimits) ou range normal(?) (ISensorLimits)
        - permitir um threshold/offset pra verificar se o valor do sensor tá *perto* de entrar nesses ranges

- [WidgetSystem]:
    - sistema de save/load de widgets
        - vai envolver coisas em outras classes tb, mas essa é o principal
    - sistema de ABAS (ou pages/tabs, whatever):
        - cada ABA tem um conjunto de Widgets
        - janela mostra uma ABA num dado momento, e só ela (só os widgets da ABA selecionada)
        - pode trocar pra outra ABA (se user configurou botão com action pra fazer isso)

- [App]:
    - pro teste inicial, criar alguns widgets hardcoded pra testar

- [Controls]
    + LCARSControl:
        * faz uma classe base que deriva de System.Windows.Controls.UserControl (deve ter atalho pra criar um UserControl e fazer isso)
        * outros controls descritos aqui irão derivar dela
        * isso é pra facilitar uso de codigo compartilhado entre as classes (se precisar), e tb facilitar limitar algum objeto a ser um "LCARS Control"
    - Button / Rect
        * common lcars rect
        + precisa suportar ter os stumps dos lados
        - precisa suportar ter uma label (com alinhamento!)
            - botao rect: alinhamento padrao é bottom-right
            - botao com stumps-both: alinhamento padrao é centro-centro
        + deve suportar os STYLES
        - pode ter comando associado
        + WPF: pode ser feito com um Border.
            + setando o CornerRadius dá pra suportar os stumps já anyway
            + setando Brush.BorderBrush pra NIL ou algo assim tiramos a borda
            + setando Brush.Background pra cor setamos o fill
                - tb dá pra setar uma imagem
    - stump
        * canto simples curvo usado pelo lcars (final de uma linha)
        - feito com shape (geometria) vetorial direto
        - deve suportar os STYLES
        - WPF: pode ser feito com um Border
        > isso talvez possa não existir, e ser só um instancia "especifica" de um Button/Rect
    - elbow
        * shape "L" curva do lcars, ligando um "rect" horizontal com um vertical
        + feito com shape (geometria) vetorial direto
        + deve suportar os STYLES
    - Label
    - Image ?
        * svg? escalada? animada?
    - ProgressBar
        - (range) min/max da barra devem ser customizaveis
            - inclusive pelo sensor associado
            - valor entao sempre será nesse range
        - talvez suportar min/max do valor do sensor?
            - tipo, alem da barra em si ter um comeco/fim (o range min/max), e mostrar aonde está o valor atual, ela poderia mostrar
              aonde nesse range tá os valores de value min/max registrados pelo sensor
            - talvez deixar esses "value min/max" customizaveis? ai poderiam ser usados pra algo alem de dados do sensor
        - suportar imagem da "barra": visual fixo da barra
        - suportar fill da barra: alguma imagem-fill, imagem-cursor ou rect-fill pra mostrar o valor atual da barra
    - Panel:
        * esse seria o grande organizador da UI... meio complexo =/
        - permite ter "bordas":
            + linha visual lcars em cima/baixo/direita/esquerda
            - permitir incluir labels em alguma seção da linha (pelo menos pra top/bottom)
            - permitir incluir botões nessa linha: sempre serao da variedade quadrada, com a linha preta separando borda|botao|borda
            + espaco interno da borda (onde pode ter labels/botoes) exclui os cantos (stump ou elbow das bordas)
            * então terá que ter algum jeito de seccionar o "espaço interno" da linha da borda, pra poder colocar a label ou botão... Como?
        + bordas desse panel devem se "encaixar" automaticamente pra definir os cantos
            + se tem bordas formando um L (tipo top+right), então ali terá um [ELBOW]
            + se o canto da borda é pra um lado *sem borda*, então ali será um [STUMP]
        + o espaço interno inteiro do panel, "dentro" das bordas (se existirem) e tal, será um unico SLOT pra um filho.
        + a borda pode ser feita internamente por um conjunto de stumps, elbows e button/rects, porem:
            + nao tem mouse-over/click! eh sempre a mesma cor
            + possivelmente a mesma cor pra todas partes de borda do mesmo panel (no minimo, para as partes de borda que estao conectadas entre si)
        - mais facil a borda ser uma coisa só, e possiveis botoes nela tem um framezinho left/right ou top/bottom preto pra fazer o "separador"
    + Axis List (Vertical/Horizontal):
        + lista de widgets organizadas verticalmente or horizontalmente, dividindo o espaço de algum jeito (padrao ser uniforme)
        + configura tamanhos (relativos) e numero de slots
        + suporta padding entre slots
        + filhos dao fill no slot deles
    - Grid:
        - conjunto ordenados de slots filhos, como as Vertical/Horizontal list, mas permitindo distribuir os widgets nos 2 eixos
        - será que precisa definir quantas colunas/rows pode ter?
            - tecnicamente daria pra determinar quantas colunas/rows precisa ter de acordo com os filhos, e aonde eles querem ficar (colunaX/rowY)
            - also, tecnicamente, se fizer uma coisa só 2x2 já deve pra boa parte dos use-cases
        - permitir um widget filho ocupar + de uma cell ao mesmo tempo.
        > a principio nao precisa desse widget. Só os Axis-Lists já resolvem a maior parte dos casos (uma grid seria uma lista-X de listas-Y, por exemplo), e sao mais faceis de implementar
    - Blank:
        - widget "nada": espaço vazio pra colocar na UI pra ajudar com a UX
        - particularmente util pra usar com a Grid/Lists acima se quiser ter um espaço diferente entre cells
    + Board:
        * separa o visual em "abas". Cada aba é uma hierarquia de LCARSControls, mas só uma fica visivel num dado momento
        + poder definir a tabela de nomes->slots
        + poder selectionar a board atual
        + habilita/mostra a board atual, esconde/desabilita todas as outras


+ [LAYOUTING] organizacão da UI
    - talvez permitir posicionar coisas por XY direto? ai ficaria meio que manual pro user se virar como quer fazer...
        - E probs teria que ser fixo pro tamanho da janela dele
    + SLOTS!
        + a janela tem um "slot" onde encaixa um widget
        + alguns widgets tem slots para filhos, assim dá pra fazer uma hierarquia
        + um slot tem o tamanho dele
            + para a raiz, é sempre o tamanho interno da janela
            + para slots de widgets, ai depende do controle mas deveria ser tamanho dinamico de acordo com o tamanho atual do controle
        * um controle sempre faz fill no espaco do seu slot
        + controles que suportam varios filhos podem ter slots dinamicos: tipo com 1 control pega tamanho (T) inteiro, com 2 controles pega T/2 e por ai vai
        + tem controles que organizam slots (tipo vertical layout, horizontal layout, grid, etc)
        > será que daria pra usar os controles existentes de C# pra isso? facilitaria bagarai implementação

+ [Estilos] de "botoes/shapes" LCARS
    * cada estilo de botao tem que:
        + precisa suportar cor fill normal da paleta lcars
        + precisa suportar cor fill mouse-hover da paleta lcars
        + precisa suportar cor fill mouse-click da paleta lcars
        + precisa suportar cor fill de desabilitado?
        + precisa suportar cor fill do texto
        + nenhum estilo/botao lcars tem borda: é só o fill acima
    * estilos que devem existir: ver conjuntos de cores (paletas) com o Fabio
        + já tá no `LCARS pallette.txt`

* [COMANDOS/ACOES] DISPONIVEIS:
    - mostrar dados de um sensor (linkado)
    - mostrar algum dado fixo (hardcoded, tipo label)
    - rodar um comando (tipo `os.system(...)`. Abrir um executavel, etc)
    - trocar de ABA

============================================================================
- precisa suportar associacao com sensores pra pegar dados deles
    - tambem precisa suportar mostrar dados fixos, mas isso tb poderia ser feito via custom "fixed" sensor, e tb via os proprios controles em si (sem associar com sensor)
- precisa suportar associar com comandos pra executarem algo


# SENSORES
- Refatorar WidgetSystem
    + transformar num Singleton
    + mudar de nome: em tese nao vamos mais usar "widgets" poderia ser LCARSSystem
    + ter a tabela de todos LCARSControls
    - flag interna pra "desabilitar" ele, e não carregar nada do hardware (isso é pra ajudar a debuggar, quando não precisamos dele podemos só "desligar")
    + metodo GetSensorsByIDs: mesma coisa do GetSensorByID, mas recebe lista de IDs, devolve lista de sensores
    + ter lista dos controles que são ILCARSSensorHandler
        + atualiza o AsyncUpdate pra chamar (ILCARSSensorHandler control).SensorBundle.AsyncUpdate
        + atualiza o Update pra chamar (ILCARSSensorHandler control).SensorBundle.Update
+ renomear pasta Widgets pra LCARS  (nao pode renomear pra System pq caga o C#)
+ Apagar coisas que não são mais necessarias:
    + as implementacoes de WidgetVisitors, a pasta onde elas estão
    + o Widget.cs em si

+ Refatorar WidgetVisitor no SensorBundle abaixo
+ SensorBundle (deriva do IVisitor)
    + tabela de ISensor
    + metodos as-is do WidgetVisitor atual
        + VisitComputer
        + VisitParameter
        + VisitHardware
        + GetSensorUnit
        + GetSensorValueFormat
        + FormatSensorString
        + GetSensorAttribute
    + metodo AsyncUpdate:
        + roda pra todo sensor na lista:
            Sensor.Hardware.Accept(Visitor);
            Sensor.Accept(Visitor);
    + metodo VisitSensor (vem do IVisitor)
        + marca qual sensor foi atualizado
    + metodo Update
        + chama pai.OnSensorUpdate pra cada sensor marcado que tá atualizado
        + limpa lista de sensores atualizados
    + tem um ILCARSSensorHandler "pai", recebido no construtor, junto com lista de IDs dos sensores que tem (ai pega eles do System)
    + chama o pai.OnSensorUpdate pra cada sensor logo que inicializa, pra atualizar as coisas no Control pai
    + isso pode não ter sensores associados! nesse caso, faz nada nas coisas

+ ILCARSSensorHandler
    + tem um SensorBundle (qual nome de property?)
    + metodo OnSensorUpdate(ISensor)
    * Control precisaria tb ter uma lista de sensor IDs e adicionar elas nos dados serializados

- Implementar o ILCARSSensorHandler nos seguintes controles:
    + Button (#1)
    - ProgressBar (#2)
    - ReactorBar (#2)
    - MainControls??? acho que nao, é mais pra comandos (mas se fosse, seria #N?)

# COMANDOS:
+ Interface System.Commands.ILCARSCommand
    + método OnRun
+ Available Commands (classes implementando ILCARSCommand):
    + Execute Stuff(?):
        + string/path de coisa pra executar? tipo `os.system`
        * ver como roda coisas assim no C#, pode facilitar
    + Change Board:
        + string TargetBoard (nome/id do Control)
        + string BoardToSelect (nome da board no control pra selecionar)
        + pegar TargetBoard pelo nome e setar o CurrentBoard dela

- tem que ser serializavel
- controles suportando comandos:
    + Button (#1)
    - MainControls (#N)
    - Communicator (#1)