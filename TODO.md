TODO

# DOCUMENTAR CLASSES E METODOS!

# STUFF
- [SensorBundle]:
    - verificar se o valor de um sensor tá no range critico (ICriticalSensorLimits) ou range normal(?) (ISensorLimits)
        - permitir um threshold/offset pra verificar se o valor do sensor tá *perto* de entrar nesses ranges

- [LCARSSystem]:
    - flag interna pra "desabilitar" o sistema: pra ajudar a debuggar, quando não precisamos dele podemos só "desligar" pra carregar mais rapido
        * permite a construção/uso das UIs
        * não carregar nada do hardware
    - metodo pra "limpar" controles não usados, tirando ref deles para que sejam apagados pelo GC
        - talvez alguma forma de chamar isso algumas hrs? Talvez pelo [Editor]?

- [EDITOR]:
    - PROBLEMAS COM EDICAO DE VALORES, coisas a arrumar:
        - string pura, na label de botao com sensor: tem umas horas que dá erro no ISensorExtensions.FormatSensorString
        - Panel, ao editar alguns campos numericos: as bordas/espaco interno não atualizavam corretamente
        - double, como nas props double do panel: o editor parece que não aceita `.` (valor com ponto flutuante)... a regex deve estar errada

    - TIPOS a suportar:
        - string (ID): verificar com o System se pode deixar tal ID, ai previne ter duplicatas

- [Controls]
    - Button / Rect
        * common lcars rect
        - Melhor suporte da LABEL
            - botao rect: alinhamento padrao é bottom-right
            - botao com stumps-both: alinhamento padrao é centro-centro
            - permitir mudar alinhamento? (alem das condicoes acima)
            - arrumar tamanho da label pra funcionar com os controles escalaveis
    - ProgressBar
        + (range) min/max da barra devem ser customizaveis
            + inclusive pelo sensor associado
            + valor entao sempre será nesse range
        + talvez suportar min/max do valor do sensor?
            + tipo, alem da barra em si ter um comeco/fim (o range min/max), e mostrar aonde está o valor atual, ela poderia mostrar
              aonde nesse range tá os valores de value min/max registrados pelo sensor
            - talvez deixar esses "value min/max" customizaveis? ai poderiam ser usados pra algo alem de dados do sensor
        + suportar imagem da "barra": visual fixo da barra
        + suportar fill da barra: alguma imagem-fill, imagem-cursor ou rect-fill pra mostrar o valor atual da barra
        + de preferencia suportar "skins" diferentes: Reactor Bar / Progress Bar (lcars) / Rects simplão
        - implementar Serializacao
        + implementar suporte a 2x Sensores (ILCARSSensorHandler)
    - Panel:
        - Implementar suporte a Buttons nas bordas:
            - permitir incluir labels em alguma seção da linha (pelo menos pra top/bottom)
            - permitir incluir botões nessa linha: sempre serao da variedade quadrada, com a linha preta separando borda|botao|borda
            * espaco interno da borda (onde pode ter labels/botoes) exclui os cantos (stump ou elbow das bordas)
            * então terá que ter algum jeito de seccionar o "espaço interno" da linha da borda, pra poder colocar a label ou botão... Como?
            * mais facil a borda ser uma coisa só, e possiveis botoes nela tem um framezinho left/right ou top/bottom preto pra fazer o "separador"
            - adicionar esses dados na Config/Dados serializados do Panel
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
        > a principio não precisa desse widget, pois permitimos Slots vazios, e os slots que ditam o tamanho/espaço dos controles


+ [SENSORES]
    - Implementar o ILCARSSensorHandler nos seguintes controles:
        + ProgressBar (#2)
        - MainControls??? acho que nao, é mais pra comandos (mas se fosse, seria #N?)

* [COMANDOS/ACOES]:
    - Implementar Suporte em:
        - MainControls (#N)
    * Serialização direta funciona sem implementar coisas extras pro json
        * talvez tenha a ver com o fato que são classes simples, somente com umas properties get/set normais.
