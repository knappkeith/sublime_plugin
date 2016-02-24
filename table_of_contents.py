import sublime, sublime_plugin
import re

class CreateContentsCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        full_text = self._get_contents()
        main_split = full_text.split('\n')
        all_headers = []
        for i in main_split:
            header = self._get_header(i)
            if header:
                all_headers.append(header)

        # print len(all_headers)
        all_headers = self._determine_indexes(all_headers)
        all_headers = self._filter_header(all_headers, level=1, index=0)
        all_headers = self._filter_header(all_headers, name='Contents')
        all_headers = self._filter_header(all_headers, level=4)
        all_headers = self._filter_header(all_headers, level=5)
        all_headers = self._filter_header(all_headers, level=6)
        if len(all_headers) == 0:
            sublime.error_message("Table of Contents is empty!")
            return False
        # print len(all_headers)
        # print all_headers
        all_headers = self._reindex_headers(all_headers, 1)
        # print all_headers
        all_headers = self._difference_is_one(all_headers)
        # print all_headers
        table = self._build_table(all_headers)
        # print table
        self.view.insert(edit, self._get_insert_point(), table)

    def is_enabled(self):
        file_name = self.view.file_name()
        if not file_name:
            sublime.error_message("Please Save file before creating Contents!")
            return False
        file_ext = self._get_file_extension(file_name)
        if file_ext == "MD":
            return True
        else:
            sublime.error_message("This file is not a Markdown File!\n\n Extension %r != %r" % (str(file_ext), "MD"))
            return False

    def _get_file_extension(self, file_name):
        a = file_name.split(".")
        if len(a) > 0:
            return a[-1].upper()
        return None

    def _get_contents(self):
        return self._get_full_contents()

    def _get_full_contents(self):
        a = self.view
        b = sublime.Region(0, a.size())
        return a.substr(b)

    def _get_insert_point(self):
        return self.view.sel()[0].begin()


    def _get_header_value(self, text_block):
        header = text_block.split('\n')[0]
        return header.strip()

    def _get_header(self, text_block):
        if re.match('^[#]{1,6}[\s]', text_block):
            header = {
                "level": len(text_block.split(' ')[0]),
                "value": " ".join(text_block.split(' ')[1:])}
            header['link'] = self._get_header_link(header['value'])
        else:
            header = None
        return header

    def _filter_header(self, headers, name=None, level=None, index=None):
        cur_index = 0
        for header in list(headers):
            if name is not None:
                if header['value'].upper() == name.upper():
                    bool_name = True
                else:
                    bool_name = False
            else:
                bool_name = True
            if level is not None:
                if header['level'] == level:
                    bool_level = True
                else:
                    bool_level = False
            else:
                bool_level = True
            if index is not None:
                if index == cur_index:
                    bool_index = True
                else:
                    bool_index = False
            else:
                bool_index = True
            if bool_name and bool_level and bool_index:
                print "filtering: %s" % header
                headers.remove(header)
                cur_index += 1
            elif bool_name and bool_level:
                cur_index += 1
        return headers

    def _reindex_headers(self, headers, level):
        offset = headers[0]['level'] - level
        index = 0
        while headers[index]['level'] != level:
            headers[index]['level'] -= offset
            index += 1
            if index >= len(headers):
                break
        return headers

    def _difference_is_one(self, headers):
        new_headers = [headers[0]]
        for i in range(1, len(headers)):
            if headers[i]['level'] > headers[i-1]['level']:
                new_headers.append(dict(headers[i]))
                new_headers[-1]['level'] = headers[i-1]['level'] + 1
            elif headers[i]['level'] == headers[i-1]['level']:
                new_headers.append(dict(headers[i]))
                new_headers[-1]['level'] = new_headers[-2]['level']
            else:
                new_headers.append(dict(headers[i]))
        return new_headers

    def _get_header_link(self, header_str):
        header = header_str.lower()
        good_chars = "abcdefghijklmnopqrstuvwxyz "
        new_header = ""
        for char in header:
            if char in good_chars:
                new_header += char
        return new_header.replace(" ", "-")

    def _determine_indexes(self, headers):
        counts = []
        for header in headers:
            header['index'] = counts.count(header['link'])
            counts.append(header['link'])
        return headers

    def _build_table(self, headers):
        bullet_str = "* "
        num_spaces = 2
        start_off = 0
        contents_str = "### Contents\n"
        for header in headers:
            indent = (num_spaces * (header['level'] - 1)) + start_off + len(bullet_str)
            link = header['link']
            if header['index'] > 0:
                link += "-%d" % header['index']
            item = "%*s[%s](#%s)\n" % (indent, bullet_str, header['value'], link)
            contents_str += item
        return contents_str
