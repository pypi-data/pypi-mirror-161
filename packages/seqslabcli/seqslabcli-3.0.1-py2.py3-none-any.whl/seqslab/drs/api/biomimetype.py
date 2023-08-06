from mimetypes import MimeTypes


class bioMimeTypes(MimeTypes):

    def __init__(self, filenames=(), strict=True):
        super().__init__(filenames=filenames, strict=strict)
        plain = ['fq', 'fastq']
        fasta = ['fa', 'fasta', 'fsa']
        tsv = ['gvcf', 'vcf', 'sam', 'bed']
        prefixs_list = [plain, fasta, tsv]
        p_mime_types = ["text/plain", "text/x-fasta", "text/tab-separated-values"]
        gzip = ['gz', 'gzip']
        zip = ['zip']
        targz = ['tar.gz', 'tgz']
        suffixs_list = [gzip, zip, targz]
        s_mime_types = ["application/gzip", "application/zip", "application/tar+gzip"]
        table = {}
        for i, prefixs in enumerate(prefixs_list):
            for _, prefix in enumerate(prefixs):
                table[f'{prefix}'] = p_mime_types[i]
                for j, suffixs in enumerate(suffixs_list):
                    for _, suffix in enumerate(suffixs):
                        table[f"{'.'.join([prefix,suffix])}"] = s_mime_types[j]
                        table[f'{suffix}'] = s_mime_types[j]

        for ext, type in table.items():
            self.add_type(type, ext, True)

    def add_type(self, type, ext, strict=True):
        """Add a mapping between a type and an extension.

        When the extension is already known, the new
        type will replace the old one. When the type
        is already known the extension will be added
        to the list of known extensions.

        If strict is true, information will be added to
        list of standard types, else to the list of non-standard
        types.
        """
        self.types_map[strict][ext] = type
        exts = self.types_map_inv[strict].setdefault(type, [])
        if ext not in exts:
            exts.append(ext)

    def mime_type(self, ext):
        for element in self.types_map:
            for key, mime_type in element.items():
                if key == ext:
                    return mime_type
        return "application/octet-stream"


def get_mime_type():
    _mime_type = bioMimeTypes()
    return _mime_type
