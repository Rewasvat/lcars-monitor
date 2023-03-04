TODO

# PASSAR TODOS PRA ISSUES NO GITHUB ???

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
    - pro teste inicial, criar alguns widgets Label hardcoded pra testar
    - definir estilo do App (minha ideia ou ideia do fabio)
        - ai atualizar essa lista para as coisas que vai precisar, tipo implementar outra janela, tray, whatever

- [Controls]
    - LCARSControl:
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
        - deve suportar os STYLES
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
            - linha visual lcars em cima/baixo/direita/esquerda
            - permitir incluir labels em alguma seção da linha (pelo menos pra top/bottom)
            - permitir incluir botões nessa linha: sempre serao da variedade quadrada, com a linha preta separando borda|botao|borda
            - espaco interno da borda (onde pode ter labels/botoes) exclui os cantos (stump ou elbow das bordas)
            * então terá que ter algum jeito de seccionar o "espaço interno" da linha da borda, pra poder colocar a label ou botão... Como?
        - bordas desse panel devem se "encaixar" automaticamente pra definir os cantos
            - se tem bordas formando um L (tipo top+right), então ali terá um [ELBOW]
            - se o canto da borda é pra um lado *sem borda*, então ali será um [STUMP]
        - o espaço interno inteiro do panel, "dentro" das bordas (se existirem) e tal, será um unico SLOT pra um filho.
        - a borda pode ser feita internamente por um conjunto de stumps, elbows e button/rects, porem:
            - nao tem mouse-over/click! eh sempre a mesma cor
            - possivelmente a mesma cor pra todas partes de borda do mesmo panel (no minimo, para as partes de borda que estao conectadas entre si)
        - mais facil a borda ser uma coisa só, e possiveis botoes nela tem um framezinho left/right ou top/bottom preto pra fazer o "separador"
    - Axis List (Vertical/Horizontal):
        - lista de widgets organizadas verticalmente or horizontalmente, dividindo o espaço de algum jeito (padrao ser uniforme)
        - talvez seja importante poder ter elementos com tamanhos diferentes... ai precisaria
            - saber os tamanhos das celulas
                - os filhos poderiam definir?
                - ou o SLOT nessa List poderia ter esse valor
                - de preferencia o "tamanho desejado" seria relativo (tipo X% do slot), altho isso probs só daria certo se o SLOT tiver o valor de tamanho
            - pega o tamanho desejado de cada celula, e normaliza eles (tipo, se forem %, e somar 120%, diminui eles igualmente pra ficar total 100%) e ai cria cells assim
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

- [LAYOUTING] organizacão da UI
    - talvez permitir posicionar coisas por XY direto? ai ficaria meio que manual pro user se virar como quer fazer...
        - E probs teria que ser fixo pro tamanho da janela dele
    - SLOTS!
        - a janela tem um "slot" onde encaixa um widget
        - alguns widgets tem slots para filhos, assim dá pra fazer uma hierarquia
        - um slot tem o tamanho dele
            - para a raiz, é sempre o tamanho interno da janela
            - para slots de widgets, ai depende do controle mas deveria ser tamanho dinamico de acordo com o tamanho atual do controle
        - um controle sempre faz fill no espaco do seu slot
        - controles que suportam varios filhos podem ter slots dinamicos: tipo com 1 control pega tamanho (T) inteiro, com 2 controles pega T/2 e por ai vai
        - tem controles que organizam slots (tipo vertical layout, horizontal layout, grid, etc)
        > será que daria pra usar os controles existentes de C# pra isso? facilitaria bagarai implementação

- [Estilos] de "botoes/shapes" LCARS
    * cada estilo de botao tem que:
        - precisa suportar cor fill normal da paleta lcars
        - precisa suportar cor fill mouse-hover da paleta lcars
        - precisa suportar cor fill mouse-click da paleta lcars
        - talvez suportar cor fill de desabilitado?
            - assim talvez seja melhor? se pá não precisaria do estilo 'desligado' abaixo
        - nenhum estilo/botao lcars tem borda: é só o fill acima
    * estilos que devem existir:
        - Normal
            - Talvez variações diferentes do normal? tipo laranja/amarelo/vermelho/azul
        - Desligado

* [COMANDOS/ACOES] DISPONIVEIS:
    - mostrar dados de um sensor (linkado)
    - mostrar algum dado fixo (hardcoded, tipo label)
    - rodar um comando (tipo `os.system(...)`. Abrir um executavel, etc)
    - trocar de ABA