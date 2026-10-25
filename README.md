# auto-rewards

O **auto-rewards** automatiza pesquisas no Microsoft Bing usando o navegador padrão e fecha as abas abertas ao final. O projeto funciona em Linux com X11 (como XFCE) e Wayland (como Hyprland), e oferece uma CLI e uma interface gráfica em CustomTkinter.

Use apenas em uma conta Microsoft já autenticada no navegador e respeite os termos aplicáveis ao serviço.

## Recursos

- CLI compacta com progresso no terminal.
- GUI em modo escuro com Start, Stop e barra de progresso.
- Quantidade de pesquisas e intervalo configuráveis.
- Configuração TOML opcional seguindo o padrão XDG.
- Modos `--dry-run` e `--verbose`.
- Detecção de sessão X11/Wayland, Hyprland e navegador.
- Cancelamento cooperativo na GUI.

## Requisitos

- Python 3.11 ou mais recente.
- Linux com X11 ou Wayland.
- Navegador disponível pelo módulo `webbrowser` do Python ou pela variável `BROWSER`.
- `xdotool` no X11 (por exemplo, XFCE) ou `ydotool` no Wayland (por exemplo, Hyprland).
- Tk, necessário para a GUI com CustomTkinter.

O programa usa `xdotool` em sessões X11 e `ydotool` em sessões Wayland para fechar as abas ao término. Mantenha o navegador em foco durante a execução e não alterne para outra janela até a finalização.

## Instalação

Clone o repositório:

```bash
git clone https://github.com/MOBSAD/auto-rewards.git
cd auto-rewards
```

A forma recomendada é instalar com `pipx`, que mantém o aplicativo isolado:

```bash
pipx install .
```

Como alternativa, instale no ambiente Python ativo:

```bash
python -m pip install .
```

O pacote instala dois comandos:

```text
auto-rewards       CLI
auto-rewards-gui   GUI
```

## Uso

### CLI

```bash
auto-rewards
auto-rewards -n 20 --delay 5
auto-rewards --dry-run
auto-rewards --verbose
auto-rewards --dry-run --verbose
```

Opções disponíveis:

| Opção | Descrição |
| --- | --- |
| `-n`, `--searches N` | Quantidade de pesquisas; deve ser um inteiro maior que zero. |
| `--delay SECONDS` | Intervalo entre pesquisas; aceita número positivo inteiro ou decimal. |
| `--dry-run` | Mostra as ações planejadas sem abrir, fechar abas ou aguardar delays. |
| `--verbose` | Mostra ambiente detectado, queries, URLs, delays e ações executadas. |
| `-h`, `--help` | Mostra a ajuda da CLI. |

Os defaults internos são 15 pesquisas e 7 segundos de intervalo.

### GUI

```bash
auto-rewards-gui
```

A GUI carrega os defaults da configuração, valida os campos e executa as pesquisas em uma thread. O botão **Stop** solicita cancelamento sem encerrar o processo à força; as abas que a execução abriu são fechadas ao final.

### Execução direta

Com as dependências instaladas, os dois modos também podem ser iniciados diretamente no repositório:

```bash
python main.py
python gui.py
```

## Configuração

A configuração é opcional e não é criada automaticamente. O caminho padrão é:

```text
~/.config/auto-rewards/config.toml
```

Quando `XDG_CONFIG_HOME` estiver definido, o caminho será:

```text
$XDG_CONFIG_HOME/auto-rewards/config.toml
```

Exemplo:

```toml
searches = 15
delay = 7
```

`searches` deve ser um inteiro maior que zero. `delay` aceita inteiro ou decimal maior que zero. TOML inválido ou valores incompatíveis produzem um erro claro.

Na CLI, a prioridade é:

```text
argumentos da CLI > config.toml > defaults internos
```

Por exemplo, `auto-rewards -n 5` substitui temporariamente um valor `searches` definido no arquivo.

## Testes

Os testes usam apenas a biblioteca padrão e não abrem navegador ou GUI:

```bash
python -m unittest
```

## Limitações

- O projeto suporta Linux com X11 e Wayland; não há suporte para macOS ou Windows.
- A detecção de Hyprland depende de `HYPRLAND_INSTANCE_SIGNATURE`.
- O navegador é aberto pelo mecanismo padrão do Python; ainda não existe opção `--browser`.
- O fechamento usa `Ctrl+W` global; o navegador deve permanecer em foco para evitar fechar uma aba não relacionada.
- A GUI permite alterar valores para a execução atual, mas não grava o arquivo de configuração.
- Stop é cooperativo: a pesquisa atual pode precisar encerrar sua etapa antes da finalização.

## Solução de problemas

### `xdotool` ou `ydotool` não encontrado

Em uma sessão X11/XFCE, instale `xdotool`. Em uma sessão Wayland/Hyprland, instale `ydotool` e mantenha `ydotoold` ativo. Consulte o gerenciador de pacotes da sua distribuição.

### Abas não fecham

Confirme que o navegador permaneceu em foco e que o utilitário correspondente à sua sessão está disponível. O programa exibirá um erro se o comando de fechamento retornar falha.

### Navegador não detectado

Confirme que existe um navegador no `PATH` ou defina `BROWSER`, por exemplo:

```bash
export BROWSER=firefox
```

### Sessão não identificada

Confira a variável usada pela detecção:

```bash
echo "$XDG_SESSION_TYPE"
```

### GUI não inicia

Confirme que a instalação incluiu `customtkinter` e que o Python possui suporte a Tk. A CLI continua disponível pelo comando `auto-rewards`.
