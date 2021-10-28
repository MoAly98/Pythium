presentation = r'''
\documentclass{{beamer}}

\mode<presentation> {{

\usetheme{{Madrid}}

}}

\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{subcaption}}
\captionsetup[sub]{{skip=0pt, font=scriptsize}}

\title[{short_title}]{{{full_title}}}

\author{{Brian LE}}
\institute[Uni of Manchester]
{{
University of Manchester
\medskip
\textit{{brian.le@cern.ch}}
}}
\date{{\today}} % Date, can be changed to a custom date

\begin{{document}}

\begin{{frame}}
\titlepage % Print the title page as the first slide
\end{{frame}}

\begin{{frame}}
\frametitle{{Overview}}
\tableofcontents
\end{{frame}}
'''

section = r'''
\section{{{section}}}
'''

subsection = r'''
\subsection{{{subsection}}}'''

page = r'''
\begin{{frame}}
\frametitle{{{title}}}
\begin{{figure}}
    \begin{{subfigure}}[t]{{.3\linewidth}}
        \includegraphics[width=\linewidth]{{{tl}}}
        \caption{{{tl_cap}}}
    \end{{subfigure}}
    \begin{{subfigure}}[t]{{.3\linewidth}}
        \includegraphics[width=\linewidth]{{{tc}}}
        \caption{{{tc_cap}}}
    \end{{subfigure}}
    \begin{{subfigure}}[t]{{.3\linewidth}}
        \includegraphics[width=\linewidth]{{{tr}}}
        \caption{{{tr_cap}}}
    \end{{subfigure}}
    \begin{{subfigure}}[t]{{.3\linewidth}}
        \includegraphics[width=\linewidth]{{{bl}}}
        \caption{{{bl_cap}}}
    \end{{subfigure}}
    \begin{{subfigure}}[t]{{.3\linewidth}}
        \includegraphics[width=\linewidth]{{{bc}}}
        \caption{{{bc_cap}}}
    \end{{subfigure}}
    \begin{{subfigure}}[t]{{.3\linewidth}}
        \includegraphics[width=\linewidth]{{{br}}}
        \caption{{{br_cap}}}
    \end{{subfigure}}
\end{{figure}}
\end{{frame}}
'''

end = r'''
\end{document}
'''
