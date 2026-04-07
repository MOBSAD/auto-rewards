# Bing Rewards Search Automator (Wayland/Arch Linux)

Este script em Python automatiza o processo de pesquisa no Microsoft Bing para acumular pontos diários no Microsoft Rewards. Ele gera termos aleatórios, abre abas no navegador padrão e as fecha automaticamente utilizando o `ydotool`.

## 🚀 Funcionalidades

* **Buscas Aleatórias**: Gera strings aleatórias para evitar padrões repetitivos de pesquisa.
* **Controle de Tempo**: Possui intervalos de espera (`sleep`) para garantir que a página carregue e os pontos sejam contabilizados.
* **Fechamento Automático**: Simula o atalho de teclado `Ctrl+W` para fechar as abas após a execução, mantendo seu navegador limpo.
* **Compatibilidade com Wayland**: Diferente de ferramentas baseadas em X11, este script utiliza o `ydotool` para funcionar corretamente em ambientes como Hyprland.

## 🛠️ Pré-requisitos

Você precisa estar com uma conta microsoft logada.
Como você está utilizando **Arch Linux**, pode instalar as dependências necessárias diretamente via terminal:

1. **Python 3**: Certifique-se de que o Python está instalado.
2. **ydotool**: Ferramenta essencial para simular entradas de teclado no Wayland.

    ```bash
    sudo pacman -S ydotool
    ```

3. **Configuração do ydotool**: O daemon precisa estar ativo para que o script funcione:

    ```bash
    ydotoold
    #eu recomendo adicionar um exec-once-ydotoold no seu .config/hypr/hyprland.conf caso use Hyprland
    ```

    *Nota: Pode ser necessário adicionar seu usuário ao grupo `input` para permissões de execução:* `sudo usermod -aG input $USER`

## 💻 Como Usar

1. **Clone o repositório**:

    ```bash
    git clone [https://github.com/MOBSAD/auto-rewards.git](https://github.com/MOBSAD/auto-rewards.git)
    cd nome-do-repo
    ```

2. **Configuração**:
    Abra o arquivo `main.py` e ajuste a variável `tabs` para a quantidade de pesquisas que deseja realizar (o padrão no script é 15).

3. **Execução**:
    Inicie o script com o navegador de sua preferência (como o Thorium) já aberto:

    ```bash
    source bin/activate
    python main.py
    ```

## ⚠️ Observações

* **Foco da Janela**: O script simula comandos de teclado globais. Certifique-se de que o navegador esteja em foco para que o fechamento das abas ocorra corretamente.
* **Segurança**: Este script foi desenvolvido para uso pessoal e automatização de tarefas simples de navegação.

## 📄 Licença

Este projeto está sob a licença MIT.
