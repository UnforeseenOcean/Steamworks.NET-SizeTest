import os
import sys
from SteamworksParser import steamworksparser

g_SkippedStructs = (
    "PSNGameBootInviteResult_t",
    "PS3TrophiesInstalled_t",
)

def OutputCPP(callbacklines, structlines):
    with open("CPPHeader.txt" , "r") as header:
        CPPHeader = header.read()

    with open("Generated/Sizes.h", "w") as out:
        out.write(CPPHeader)
        for line in callbacklines:
            out.write(line + '\n')
        out.write('\tfs << ("=================================================\\n");\n')
        for line in structlines:
            out.write(line + '\n')
        out.write('\tfs << ("=================================================\\n");\n')
        out.write('\tfs.close();\n')
        out.write('}\n')  # Namespace

def OutputCSharp(callbacklines, structLines):
    with open("CSharpHeader.txt", "r") as header:
        CSharpHeader = header.read()

    with open("Generated/Sizes.cs", "w") as out:
        out.write(CSharpHeader)
        for line in callbacklines:
            out.write(line + '\n')
        out.write('\t\t\tlines.Add("=================================================");\n')
        for line in structLines:
            out.write(line + '\n')
        out.write('\t\t\tlines.Add("=================================================");\n')
        out.write("\t\t\tSystem.IO.File.WriteAllLines(path + filename, lines.ToArray());\n")
        out.write("\t\t}\n")
        out.write("\t}\n")
        out.write("}\n")

def ParseCSharp(struct):
    offsets = ''
    if struct.fields:
        offsets = ' + ", Offsetof: "'
        offsets += ' + ", "'.join([' + Marshal.OffsetOf(typeof({0}), "{1}")'.format(struct.name, field.name) for field in struct.fields])
    return '\t\t\tlines.Add("{0}, Sizeof: " + Marshal.SizeOf(typeof({0})){1});'.format(struct.name, offsets)

def ParseCpp(struct):
    offsets = '\tfs << "{0}, Sizeof: " << sizeof({0}) << '.format(struct.name)
    if len(struct.fields) > 0:
        offsets += ' ", Offsetof: " << '
    for i, f in enumerate(struct.fields):
        offsets += 'offsetof({0}, {1}) << '.format(struct.name, f.name)
        if i != len(struct.fields) - 1:
            offsets += '", " << '
    offsets += '"\\n";'
    return offsets

def main(parser):
    try:
        os.makedirs('Generated/')
    except OSError:
        pass

    csharpLines = []
    structLines = []
    cppcallbackLines = []
    cppcStructLines = []
    for f in parser.files:
        for callback in f.callbacks:
            if callback.name in g_SkippedStructs:
                continue
            csharpLines.append(ParseCSharp(callback))
            cppcallbackLines.append(ParseCpp(callback))
        for struct in f.structs:
            if callback.name in g_SkippedStructs:
                continue
            structLines.append(ParseCSharp(struct))
            cppcStructLines.append(ParseCpp(struct))
    OutputCSharp(csharpLines, structLines)
    OutputCPP(cppcallbackLines, cppcStructLines)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(steamworksparser.parse(sys.argv[1]))
    else:
        print("Usage: Steamworks.NET_CodeGen.py path/to/steamworks_header_folder/")

