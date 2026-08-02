if not status is-interactive
    return
end

/opt/homebrew/bin/brew shellenv | source

# You must call it on initialization or listening to directory switching won't work
load_nvm > /dev/stderr

direnv hook fish | source
starship init fish | source
zoxide init fish | source
atuin init fish | source

# set -gx PATH $HOME/.local/bin $PATH
fish_add_path $HOME/.local/bin
fish_add_path $HOME/.npm/bin

# aliases
alias lsla="ls -la"
alias size="du -hsc *"

# tools
alias gmj="gitmoji -c"
alias lg="lazygit"

alias gmc="git-cz"
alias gcz="git-cz"

alias prs="gh search prs --owner humanitec --state open --author @me"

# projects
alias projects="cd ~/Projects"
alias pet="cd ~/Projects/Personal"
alias brain="cd ~/Documents/Obsidian/brain"
alias ht="cd ~/Projects/Humanitec"

# docker
alias dcleannone='docker rmi (docker images | grep "<none>" | awk \'{print $3}\')'
alias dstopall='docker ps -a | awk \'{print $1}\' | tail -n +2 | xargs docker stop'
alias dremoveall='docker ps -a | awk \'{print $1}\' | tail -n +2 | xargs docker rm -fv'

# kubernetes
alias k='kubectl'
alias kd='kubectl describe'
alias kdd='kubectl describe deployment'
alias kdp='kubectl describe pod'
alias kei='kubectl exec -it'
alias kg='kubectl get'
alias kgall='kubectl get --all-namespaces all'
alias kgd='kubectl get deployments'
alias kgp='kubectl get pod'
alias kgsvc='kubectl get service'
alias kl='kubectl logs --all-containers=true'
alias krm='kubectl delete'

# misc infra
alias tf='tofu'
alias ggc='gcloud'

# default programs
set -gx TERMINAL ghostty

# gcloud
set -gx PATH $PATH ~/google-cloud-sdk/bin

# go
# set -gx PATH /opt/homebrew/opt/go@1.24/bin $PATH
# or
fish_add_path /opt/homebrew/opt/go@1.24/bin

set -Ux CARAPACE_BRIDGES 'zsh,fish,bash,inshellisense' # optional
carapace _carapace | source


source /opt/homebrew/opt/asdf/libexec/asdf.fish
set -gx PATH /opt/homebrew/opt/postgresql@17/bin $PATH
