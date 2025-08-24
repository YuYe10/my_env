" modified: 2025/03/12
" set coloscheme and fonts
" colorscheme gruvbox
" set guifont=Source\ Code\ Pro:h16

" map leader as ,
let mapleader=","


" for the normal mode of chinese input
set encoding=utf-8
set fileencodings=ucs-bom,utf-8,cp936,gb18030


" the number of the line
set number
set hidden
set mouse=a
set cursorline
hi CursorLine cterm=NONE ctermbg=darkgrey

" change the windows
nnoremap <C-p> <C-w><C-w>


" auto insert mode
function g:Auto_ins() abort
if col('.') == col('$')-1
    call feedkeys('a', 'n')
else
    call feedkeys('i', 'n')
endif
endfunction

" the move keys IJKL
inoremap jj <Esc>
inoremap JJ <Esc>

nnoremap <Space><Space> :call g:Auto_ins()<cr>


" just use microssoft's shortcut
source $VIMRUNTIME/mswin.vim
if !has("clipboard")
vnoremap <C-x> +d 
endif
inoremap <C-s> <Esc>:w<cr>
nnoremap <C-q> :term<cr>


" Auto close the buffer
autocmd Bufenter * if ( len(filter(range(1, bufnr('$')), 'buflisted(v:val)')) == 1 ) | nnoremap <C-w> :q<cr> | else | nnoremap <C-w> :bw<cr> | endif 

" load pluggins
call plug#begin('~/.vim/plugged')

" the bar which is in top and buttom
Plug 'vim-airline/vim-airline'
Plug 'vim-airline/vim-airline-themes'

let g:airline#extensions#tabline#enabled=1
let g:airline#extensions#tabline#buffer_nr_show=0
let g:airline#extensions#tabline#left_sep=' '
let g:airline#extensions#tabline#left_alt_sep='|'
let g:airline#extensions#tabline#formatter='unique_tail'
let g:airline#extensions#whitespace#enabled=0
let g:airline_section_z='(%l,%c) - %L*%2p%%'


" the visible of the space and tab
set tabstop=4
set shiftwidth=4
set tabstop=4
set expandtab
Plug 'yggdroot/indentline'


" the paired parentheses
let g:AutoPairsMapBS = 0
Plug 'jiangmiao/auto-pairs'
Plug 'luochen1990/rainbow'
let g:rainbow_active = 1 "set to 0 if you want to enable it later via :RainbowToggle:
let g:rainbow_conf = {
\	'guifgs': ['royalblue3', 'darkorange3', 'seagreen3', 'firebrick'],
\	'ctermfgs': ['lightblue', 'lightyellow', 'lightcyan', 'lightmagenta'],
\	'operators': '_,_',
\	'parentheses': ['start=/(/ end=/)/ fold', 'start=/\[/ end=/\]/ fold', 'start=/{/ end=/}/ fold'],
\	'separately': {
\		'*': {},
\		'tex': {
\			'parentheses': ['start=/(/ end=/)/', 'start=/\[/ end=/\]/'],
\		},
\		'lisp': {
\			'guifgs': ['royalblue3', 'darkorange3', 'seagreen3', 'firebrick', 'darkorchid3'],
\		},
\		'vim': {
\			'parentheses': ['start=/(/ end=/)/', 'start=/\[/ end=/\]/', 'start=/{/ end=/}/ fold', 'start=/(/ end=/)/ containedin=vimFuncBody', 'start=/\[/ end=/\]/ containedin=vimFuncBody', 'start=/{/ end=/}/ fold containedin=vimFuncBody'],
\		},
\		'html': {
\			'parentheses': ['start=/\v\<((area|base|br|col|embed|hr|img|input|keygen|link|menuitem|meta|param|source|track|wbr)[ >])@!\z([-_:a-zA-Z0-9]+)(\s+[-_:a-zA-Z0-9]+(\=("[^"]*"|'."'".'[^'."'".']*'."'".'|[^ '."'".'"><=`]*))?)*\>/ end=#</\z1># fold'],
\		},
\		'css': 0,
\		'nerdtree': 0,
\	}
\}


" the file tree 
Plug 'scrooloose/nerdtree'
nnoremap <F3> :NERDTreeMirror<CR>
nnoremap <F3> :NERDTreeToggle<CR>

"打开vim时如果没有文件自动打开NERDTree
autocmd vimenter * if !argc()|NERDTree|endif
"当NERDTree为剩下的唯一窗口时自动关闭
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif

"set the icon of the tree
let g:NERDTreeDirArrowExpandable = '▸'
let g:NERDTreeDirArrowCollapsible = '▾'
" ignore some types of files
let NERDTreeIgnore = ['\.pyc$', '\.swp', '\.swo', '\.vscode', '__pycache__']
let g:NERDTreeShowLineNumbers=0  " 是否显示行号
let g:NERDTreeHidden=0     " 不显示隐藏文件
let NERDTreeQuitOnOpen=1   " 打开文件后自动关闭NERDTree

" code runner
let g:asynctasks_term_pos = 'bottom'
let g:asynctasks_term_rows = 8
Plug 'skywind3000/asyncrun.vim'
Plug 'skywind3000/asynctasks.vim'
nnoremap <C-r> :AsyncTask file-run<cr>
inoremap <C-r> <Esc>:w<cr>:AsyncTask file-run<cr>

" use tab to complete
" if v:version >= 900 
"    if has("linux")
"        Plug 'github/copilot.vim'
"    else
"        Plug 'WuJunkai2004/fittencode.vim', { 'branch': 'AutoCompletion' }
"    endif
" else
"    Plug 'ervandew/supertab', { 'commit': 'a9dab76' }
" endif

" the better search and replace
set hlsearch
set incsearch
set ignorecase
set smartcase
Plug 'romainl/vim-cool'
Plug 'PeterRincker/vim-searchlight'

" better buffer changed
let g:airline#extensions#tabline#fnametruncate=16
let g:airline#extensions#tabline#fnamecollapse=2
let g:airline#extensions#tabline#buffer_idx_mode=1

" let g:cangjie_identifier_color = 0
" let g:cangjie_lsp_config = 'intime'
" Plug 'https://gitcode.com/Neila/cangjie.vim.git'

function g:Buf_switch(num) abort
    let l:buf_goal=a:num
    let l:buf_index=a:num
    let l:buf_list=filter(range(1, bufnr('$')), 'buflisted(v:val)')
    for idx in range(len(l:buf_list))
        if getbufvar(l:buf_list[idx], '&buftype') ==# 'quickfix'
            call remove(l:buf_list, idx)
            break
        endif
    endfor
    let l:buf_count=len(l:buf_list)
    if a:num > l:buf_count
        return 
    endif
    execute ':b'.l:buf_list[l:buf_goal-1]
endfunction
nnoremap <leader>1 :call g:Buf_switch(1)<cr>
nnoremap <leader>2 :call g:Buf_switch(2)<cr>
nnoremap <leader>3 :call g:Buf_switch(3)<cr>
nnoremap <leader>4 :call g:Buf_switch(4)<cr>
nnoremap <leader>5 :call g:Buf_switch(5)<cr>
nnoremap <leader>6 :call g:Buf_switch(6)<cr>
nnoremap <leader>7 :call g:Buf_switch(7)<cr>
nnoremap <leader>8 :call g:Buf_switch(8)<cr>
nnoremap <leader>9 :call g:Buf_switch(9)<cr>
nnoremap <leader>0 :call g:Buf_switch(10)<cr>

call plug#end()
