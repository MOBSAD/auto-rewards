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

1. **Python 3.11 ou mais recente**: O projeto usa `tomllib`, incluído na biblioteca padrão a partir do Python 3.11.
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
    git clone https://github.com/MOBSAD/auto-rewards.git
    cd auto-rewards
    ```

2. **Execução**:
    Inicie o script com o navegador de sua preferência (como o Thorium) já aberto:

    ```bash
    python main.py
    ```

    Por padrão, são realizadas 15 pesquisas com intervalo de 7 segundos. As opções disponíveis podem ser consultadas com:

    ```bash
    python main.py --help
    ```

    Exemplos:

    ```bash
    python main.py -n 20 --delay 5
    python main.py --dry-run
    python main.py --verbose
    python main.py --dry-run --verbose
    ```

## ⚙️ Configuração persistente

A configuração é opcional. Quando presente, o arquivo deve ficar em:

```text
~/.config/auto-rewards/config.toml
```

Se `XDG_CONFIG_HOME` estiver definido, o caminho usado será:

```text
$XDG_CONFIG_HOME/auto-rewards/config.toml
```

Exemplo:

```toml
searches = 15
delay = 7
```

`searches` deve ser um número inteiro maior que zero. `delay` aceita um número inteiro ou decimal maior que zero. O arquivo não é obrigatório nem criado automaticamente.

Os valores são escolhidos nesta ordem de prioridade:

```text
argumentos da CLI > config.toml > defaults internos
```

Por exemplo, com `searches = 15` no arquivo, `python main.py -n 5` executa cinco pesquisas.

## ⚠️ Observações

* **Foco da Janela**: O script simula comandos de teclado globais. Certifique-se de que o navegador esteja em foco para que o fechamento das abas ocorra corretamente.
* **Segurança**: Este script foi desenvolvido para uso pessoal e automatização de tarefas simples de navegação.

## 📄 Licença

Este projeto está sob a licença MIT.
