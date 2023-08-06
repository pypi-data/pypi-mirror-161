// compile with
// f=ckvh; c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3.8 -m pybind11 --includes) $f.cpp -o $f$(python3.8-config --extension-suffix)
#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)

#include <Python.h>
#include <pybind11/pybind11.h>
namespace py = pybind11;

#include <cstdio>
#include <cerrno>
#include <string>
#include <set>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cerrno>
#include <algorithm>

#include "ckvh.h"

static std::string whitespaces(" \t\f\v\n\r");
//py::object op = py::module_::import("os.path");

//py::object dn = op.attr("dirname");
//py::object bn = op.attr("basename");
//py::object np = op.attr("normpath");

// auxiliary functions
bool starts_with(std::string s, std::string pre) {
    if (pre.size() > s.size())
        return false;
    return s.substr(0, pre.size()) == pre;
}
inline bool is_ap(const std::string &p) {
    // chack if a path is absolute one
    return starts_with(p, "/") || (isalpha(p[0]) && (starts_with(p.substr(1), ":/") || starts_with(p.substr(1), ":\\")));
}
template <typename T>
std::string join(std::vector<T> v, std::string sep) {
    std::ostringstream res;
    for (typename std::vector<T>::iterator ii=v.begin(); ii != v.end(); ++ii)
        res << *ii << (ii+1 != v.end() ? sep : "");
    return res.str();
}
std::vector<std::string> split(const std::string &s, const std::string &sep) {
    std::vector<std::string> vs; // will have results of split
    size_t pos, splpos; // position of the split string in s
    std::string subs;
    for (pos=0; pos < s.size() && (splpos=s.find(sep, pos)) != std::string::npos; pos = splpos+sep.size())
        vs.push_back(s.substr(pos, splpos-pos));
    vs.push_back(s.substr(pos)); // add the last field at the end of s
    return vs;
}
std::string dir_n(std::string p) {
    // extract dirname part of path p
    auto i=p.find_last_of("/");
    if (i == std::string::npos)
        return std::string(".");
    else
        return p.substr(0, i);
    //return py::str(dn(p.c_str()));
}
std::string base_n(std::string p) {
    // extract basename part of path p
    return p.substr(p.find_last_of("/") + 1);
    //return py::str(bn(p.c_str()));
}
std::string norm_p(std::string p) {
    // normalize path p: //... -> /; /./ -> /; /foo/../baz/ -> /baz
    std::vector<std::string> vs;
    vs=split(p, "/");
    //Rcout << "vs=" << std::endl;
    //for (auto s: vs)
    //    Rcout << "\t" << s << std::endl;
    // remove empty items (i.e. repeated '/') and '.'
    if (vs.size() == 0)
        return "";
    if (vs[0] == "") // keep the first '/' in absolute path
        vs.erase(std::remove_if(vs.begin()+1, vs.end(), [&](const std::string& s) {
            return s.size() == 0 || s == ".";
        }), vs.end());
    else
        vs.erase(std::remove_if(vs.begin(), vs.end(), [&](const std::string& s) {
            return s.size() == 0 || s == ".";
        }), vs.end());
    // remove '..'
    for (auto i=std::find(vs.begin(), vs.end(), ".."); i != vs.end(); i=std::find(vs.begin(), vs.end(), "..")) {
        int ii=std::distance(vs.begin(), i);
        if (ii == 0)
            throw std::runtime_error("in a path '" + p + "' there are too many '..' as they point upper then the beginning of the path.");
        vs.erase(vs.begin()+ii-1, i+1);
    }
    return join(vs, "/");
    //return py::str(np(p.c_str()));
}

std::string unescape(std::string s) {
    // unescape tab, newline and backslash
    std::string res=s;
    size_t i,j;
    char c;
    for (i=0,j=0; i < s.size(); i++) {
        if (s[i] == '\\') {
            if (i < s.size()-1) {
                c=s[i+1];
                // unescape only these three chars
                res[j++]=(c == '\\' || c == '\t' || c == '\n') ? s[++i] : s[i];
            }
        } else {
            res[j++]=s[i];
        }
    }
    return res.substr(0, j);
}
bool indent_lacking(std::string& buf, size_t& lev) {
    // check if number of starting tab corresponds to lev
    if (lev == 0)
        return false; // at level 0 no lacking tabs
    if (buf.size() < lev)
        return true; // too short to have sufficient number of tabs
    for (size_t i=0; i < lev; i++) {
        if (buf[i] != '\t')
            return true;
    }
    return false;
}
bool escaped_eol(std::string& buf) {
    // test if end_of_line is escaped or not in buf
    int i;
    if (buf.size() == 0)
        return false;
    for (i=buf.size()-1; i >= 0 && buf[i] == '\\'; i--) {
        ; // find out the position of the last backslash series
    }
    i=buf.size()-i-1;
    return i%2;
}
inline void strip_wh(std::string &s) {
    if (s.size() == 0)
        return;
    size_t pstr;
    pstr=s.find_first_not_of(whitespaces);
    if (pstr != std::string::npos) {
        s.erase(0, pstr);
    } else {
        s.clear(); // s is all whitespace
        return;
    }
    pstr=s.find_last_not_of(whitespaces);
    if (pstr != std::string::npos)
        s.erase(pstr+1);
    return;
}
std::string kvh_get_line(std::istream& fin, size_t* ln, const std::string& comment_str) {
    // get a string from stream that ends without escaped eol character and increment ln[0]
    std::string b, res;
    size_t pstr;
    res="";
    //bool first_read=true;
    //ssize_t nch;
    while (!fin.eof()) {
        std::getline(fin, b);
        ln[0]++;
        //if (bchar[nch-1] == '\n')
        //    bchar[nch-1]=0;
        res += b;
        if (escaped_eol(b) && !fin.eof())
            res += '\n';
        else
            break;
    }
    if (comment_str.size() > 0) {
        pstr=res.find(comment_str);
        if (pstr != std::string::npos && (b=res.substr(0, pstr), true) && !escaped_eol(b)) // stip out non escaped comments
            res=b;
    }
    return res;
}
keyval kvh_parse_kv(std::string& line, size_t& lev, const bool strip_white, const std::string &split_str) {
    // get key-value pair from the line
    keyval kv;
    size_t i, bs; // count backslashes;
    std::string s;
    for (i=lev, bs=0; i < line.size(); i++) {
        if (line[i] == '\\') {
            bs++;
            continue;
        }
        if (line[i] == '\t' && (bs+1)%2) {
            kv.key=unescape(line.substr(lev, i-lev));
            if (strip_white) {
                strip_wh(kv.key);
            }
            s=line.substr(i+1);
            if (split_str.size() > 0) {
                // split s
                std::vector<std::string> vs; // will have results of split
                size_t pos, splpos; // position of the split string in s
                std::string subs;
                for (pos=0; pos < s.size() && (splpos=s.find(split_str, pos)) != std::string::npos;) {
                    for (subs=s.substr(pos, splpos-pos); escaped_eol(subs) && splpos != std::string::npos; splpos=s.find(split_str,  splpos+split_str.size()), subs=s.substr(pos, splpos-pos))
                        ; // find first unescaped splpos
                    if (strip_white)
                        strip_wh(subs);
                    vs.push_back(unescape(subs));
                    pos=splpos+split_str.size();
                }
                subs=s.substr(pos);
                if (strip_white)
                    strip_wh(subs);
                vs.push_back(unescape(subs)); // add the last field at the end of s
                if (vs.size() > 1) {
                    py::tuple vs_r((size_t) vs.size());
                    for (size_t i=0; i < vs.size(); i++)
                        vs_r[i]=py::str(vs[i]);
                    //py::tuple vs_r=py::make_tuple(vs);
                    kv.val=py::object(vs_r);
                } else {
                    kv.val=py::object(py::str(vs[0]));
                }
            } else {
                if (strip_white)
                    strip_wh(s);
                kv.val=py::str(s);
            }
            kv.tab_found=true;
            break;
        }
        bs=0;
    }
    if (i == line.size()) {
        // no tab found => the whole string goes to the key
        kv.key=unescape(line.substr(lev));
        if (strip_white) 
            strip_wh(kv.key);
        kv.val=py::str("");
        kv.tab_found=false;
    }
    return(kv);
}
list_line kvh_read(std::istream& fin, size_t lev, size_t* ln, const std::string& comment_str, const bool strip_white, const bool skip_blank, const std::string& split_str, const bool follow_url) {
    // recursively read kvh file and return its content in a nested named list of character vectors
    py::list res;
    keyval kv;
    std::string line;
    list_line ll;
    bool read_stream=true;
    //size_t ln_save;
    //py::list nm(0);
    while (!fin.eof()) { // && i++ < 5) {
        // get full line (i.e. concat lines with escaped end_of_line)
        if (read_stream) {
            /*
            #ifdef _WIN32
            #include <Windows.h>
            #else
            #include <unistd.h>
            #endif
            sleep(1);
            */
            line=kvh_get_line(fin, ln, comment_str);
            if (ln[0] % 100 == 0 && PyErr_CheckSignals() != 0)
                throw std::runtime_error(std::string("interrupted by Ctrl-C"));
        }
        if (skip_blank && (line.size() == 0 || (strip_white && line.find_first_not_of(whitespaces) == std::string::npos)) && !fin.eof()) {
            continue; // skip white line
        }
        if ((line.size() == 0 && fin.eof()) || (lev && indent_lacking(line, lev))) {
            // current level is ended => go upper and let treat the line (already read) there
            //res.attr("ln")=(int) ln[0];
            //res.attr("names")=nm;
            //for (size_t i=0; i < res.size(); i++) {
            //    res[i]=py::make_tuple(nm[i], res[i]);
            //}
            ll.res=res;
            ll.line=line;
            return ll;
        }
        kv=kvh_parse_kv(line, lev, strip_white, split_str);
        //ln_save=ln[0];
        read_stream=kv.tab_found;
        if (!kv.tab_found) {
            // tab is absent => we have to go deeper in the hierarchy level
            ll=kvh_read(fin, lev+1, ln, comment_str, strip_white, skip_blank, split_str, follow_url);
            kv.val=(ll.res.size() == 0 ? py::object(py::str("")) : py::object(ll.res));
            line=ll.line;
        } // else simple key-value pair
        if (follow_url && py::isinstance<py::str>(kv.val)) { //kv.val.sexp_type() == STRSXP
            std::string sval=py::str(kv.val);
            if (sval.substr(0, 7) == "file://") {
                kv.val=kvh_read(sval.substr(7), comment_str, strip_white, skip_blank, split_str, follow_url);
                if (py::isinstance<py::none>(kv.val)) {
                    kv.val=py::object(py::str(sval));
                }
            }
        } // else if (kv.val.sexp_type() == STRSXP) { CharacterVector cval(kv.val); std::string sval=as<std::string>(cval[0]); if (sval.substr(0, 7) == "file://") Rcout << "not following '" << sval << "'\n";}
        //kv.val.attr("ln")=(int) ln_save;
        res.append(py::make_tuple(py::str(kv.key), kv.val));
        //nm.append(py::str(kv.key));
    }
    //res.attr("names")=nm;
    //for (size_t i=0; i < res.size(); i++) {
    //    res[i]=py::make_tuple(nm[i], res[i]);
    //}
    ll.res=res;
    ll.line="";
    return ll;
}
py::object kvh_read(std::string fn, const std::string& comment_str="", const bool strip_white=false, const bool skip_blank=false, const std::string& split_str="", const bool follow_url=false) {
    if (fn.size() == 0)
        throw std::runtime_error("kvh_read: file name is empty");
    // read kvh file and return its content in a nested named list of character vectors
    if (comment_str.find('\t') < std::string::npos || comment_str.find('\n') < std::string::npos) {
        throw std::runtime_error("kvh_read: parameter 'comment_str' cannot have tabulation or new line characters in it");
    }
    // check for nested references if follow_url=true
    static std::set<std::string> read_files;
    static std::vector<std::string> dirw;
    bool absp=is_ap(fn);
    std::string dn=dir_n(fn);
    std::string npath;
    if (follow_url) {
        dirw.push_back(absp || dirw.size() == 0 ? dn : dirw[dirw.size()-1]+"/"+dn);
        fn=dirw[dirw.size()-1]+"/"+base_n(fn);
        npath=norm_p(fn);
        if (read_files.count(npath)) {
            std::cerr << "kvh_read: detected circular reference to file '" << npath << "' via '" << fn << "'" << std::endl;
            return py::none();
        }
        read_files.insert(npath);
    }
    // open file for binary reading
    std::ifstream fin;
    list_line ll;
    size_t ln=0; // running line number in kvh file
    fin.open(fn.c_str(), std::ios_base::binary);
    if (!fin.good()) {
        if (follow_url) {
            read_files.erase(npath);
            dirw.pop_back();
        }
        throw std::runtime_error(std::string("kvh_read: cannot read in file '")+fn.c_str()+"'; the reason: "+std::strerror(errno));
    }
    ll=kvh_read(static_cast<std::istream&>(fin), 0, &ln, comment_str, strip_white, skip_blank, split_str, follow_url);
    fin.close();
    if (follow_url) {
        read_files.erase(npath);
        dirw.pop_back();
    }
    //ll.res.attr("file")=fn;
    return ll.res;
}
PYBIND11_MODULE(ckvh, m) {
    using namespace pybind11::literals;
    m.doc() = "read a file in KVH format (developed in C++)"; // module docstring
    m.def("kvh_read",  (py::object (*)(std::string, const std::string&, const bool, const bool, const std::string&, const bool)) &kvh_read, "fn"_a, "comment_str"_a="", "strip_white"_a=false, "skip_blank"_a=false, "split_str"_a="", "follow_url"_a=false, R"mydelimiter(
    Parse file in KVH format
    
    :param fn: character or FILE*, kvh file name or an input stream
    :param comment_str: character, optional comment string (default empty ""). If non empty, the comment string itself and everything following it on the line is ignored. Note that lines are first appended if end lines are escaped and then a search for a comment string is done.
    :param strip_white: logical, optional control of white spaces on both ends of keys and values (default False)
    :param skip_blank: logical, optional control of lines composed of only white characters after a possible stripping of a comment (default False)
    :param split_str: character, optional string by which a value string can be splitted in several strings (default: empty string, i.e. no splitting)
    :param follow_url: logical, optional control of recursive kvh reading and parsing. If set to True and a value starts with 'file://' then the path following this prefix will be passed as argument 'fn' to another 'kvh_read()' call. The list returned by this last call will be affected to the corresponding key instead of the value 'file://...'. If a circular reference to some file is detected, a warning is emmited and the faulty value 'file://...' will be left without change. The rest of the file is proceeded as usual. If a path is relative one (i.e. not strating with `/` neither 'C:/' or alike on windows paltform) then its meant relative to the location of the parent kvh file, not the current working directory.
    :return: list of tuples (key, value) where 'key' is always a string, and 'value' can be a string, a list of tuples or a tuple (if 'split_str' is not empty and there are more then one item).

)mydelimiter");
    m.def("kvh_read", [](py::object fp, const std::string& comment_str, const bool strip_white, const bool skip_blank, const std::string& split_str, const bool follow_url) {
        if (!(py::hasattr(fp,"read") && py::hasattr(fp,"flush")))
            throw py::type_error("kvh_read: incompatible function argument: 'fp' must be a string or file-like object, but `"+(std::string)(py::repr(fp))+"` provided");
        std::istringstream sin(fp.attr("read")().cast<std::string>());
        size_t ln=0;
        return kvh_read(static_cast<std::istream&>(sin), 0, &ln, comment_str, strip_white, skip_blank, split_str, follow_url).res;
    }, "fp"_a, "comment_str"_a="", "strip_white"_a=false, "skip_blank"_a=false, "split_str"_a="", "follow_url"_a=false);
#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
