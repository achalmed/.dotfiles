// Resaltado — KSyntaxHighlighting para un TextArea (el diff de un cambio); en archivo aparte para que, si el módulo
// `org.kde.syntaxhighlighting` no está instalado, el texto se vea plano (lo carga un Loader).
import QtQuick
import org.kde.syntaxhighlighting

SyntaxHighlighter {
    property string nombreDefinicion: "Diff"
    definition: Repository.definitionForName(nombreDefinicion)
}
