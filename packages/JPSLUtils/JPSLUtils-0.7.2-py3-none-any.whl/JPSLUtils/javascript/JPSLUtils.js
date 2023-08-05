// Jupyter Notebook Utilities
JPSLUtils = new Object();
/*
Initialization
*/
JPSLUtils.env = "None";

JPSLUtils.init = function(){
    // Run all input table cells to make sure the tables are showing and
    // active. Also hide the table creation code.
    JPSLUtils.hide_input_table_code();
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.input_table_cell==true){
                celllist[i].execute();
            }
        }
    }
    // Hide the code for cells marked with metadata.JPSL.hide_code = true.
    JPSLUtils.hide_hide_code_code();
};

JPSLUtils.getenv = function(){
    if (typeof (Jupyter) != 'undefined'){
        JPSLUtils.env = "NBClassic";
        Jupyter.notebook.kernel.execute('JPSLUtils.notebookenv = "'+JPSLUtils.env+'"');
    } else {
        var configscript = document.getElementById("jupyter-config-data");
        if (configscript){
            var config = JSON.parse(configscript.innerText);
            var name = config['appName'];
            if (name){
                JPSLUtils.env = name;
            }
        }
    }
};

/*
Latex utilities
*/

JPSLUtils.pseudoLatexToLatex = function(text){
    text = text.replaceAll('%FRAC','\\frac');
    text = text.replaceAll('%EXP','\\exp');
    text = text.replaceAll('%SIN','\\sin');
    text = text.replaceAll('%LEFT','\\left');
    text = text.replaceAll('%RIGHT','\\right');
    text = text.replaceAll('%SQRT','\\sqrt');
    text = text.replaceAll('%PI','\\pi');
    text = text.replaceAll('%COLOR','\\color');
    return(text);
};

/*
Cell Utilities
*/

JPSLUtils.select_containing_cell = function(elem){
    //Create a synthetic click in the cell to force selection of the cell
    // containing the element (elem).
    var event = new MouseEvent('click', {
    view: window,
    bubbles: true,
    cancelable: true
    });
    var cancelled = !elem.dispatchEvent(event);
    if (cancelled) {
    // A handler called preventDefault.
    alert("Something is wrong. Try rerunning the cell.");
    }
};

JPSLUtils.select_cell_immediately_below = function(){
    Jupyter.notebook.select_next(true);
};

JPSLUtils.text_of_current_cell_to_Python = function(varName){
    var text = Jupyter.notebook.get_selected_cell().get_text();
    if (typeof (text) == 'undefined'){
        text = '';
    }
    var cmdstr = '"'+varName+' = \"'+ text +'\""';
    //alert (cmdstr);
    JPSLUtils.wait_for_python('\'' + cmdstr+'\'');
        //.then(resolve => JPSLUtils.wait_for_python(
        //'print(JPSLUtils.return_text_of_current_cell())');
        //.then(reject => alert(reject));
};

JPSLUtils.replace_text_of_current_cell = function(text){
    text = JPSLUtils.pseudoLatexToLatex(text);
    Jupyter.notebook.get_selected_cell().set_text(text);
};

JPSLUtils.insert_newline_at_end_of_current_cell = function(text){
    var lastline = Jupyter.notebook.get_selected_cell().code_mirror.doc.
        lineCount();
    Jupyter.notebook.get_selected_cell().code_mirror.doc.setCursor(lastline,0);
    Jupyter.notebook.get_selected_cell().code_mirror.doc.
         replaceSelection("\n" + text);
};

JPSLUtils.insert_text_at_beginning_of_current_cell = function(text){
    // append \n to line insert as a separate line.
    Jupyter.notebook.get_selected_cell().code_mirror.doc.
           setCursor({line:0,ch:0});
    Jupyter.notebook.get_selected_cell().code_mirror.doc.
           replaceSelection(text);
};

JPSLUtils.hide_hide_on_print_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL){
            if (celllist[i].metadata.JPSL.hide_on_print==true){
                celllist[i].element[0].classList.add("hidden");
            }
        }
    }
    JPSLUtils.hide_hide_code_on_print_code();
};

JPSLUtils.show_hide_on_print_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL){
            if (celllist[i].metadata.JPSL.hide_on_print==true){
                celllist[i].element[0].classList.remove("hidden");
            }
        }
    }
        JPSLUtils.show_hide_code_on_print_code();
};

JPSLUtils.hide_input_table_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.input_table_cell==true){
                celllist[i].input[0].classList.add("hidden");
            }
        }
    }
};

JPSLUtils.show_input_table_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.input_table_cell==true){
                celllist[i].input[0].classList.remove("hidden");
            }
        }
    }
};

JPSLUtils.hide_hide_code_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code==true){
                celllist[i].input[0].classList.add("hidden");
            }
        }
    }
};

JPSLUtils.show_hide_code_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code==true){
                celllist[i].input[0].classList.remove("hidden");
            }
        }
    }
};

JPSLUtils.hide_hide_code_on_print_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code_on_print==true){
                celllist[i].input[0].classList.add("hidden");
            }
        }
    }
};

JPSLUtils.show_hide_code_on_print_code = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL && celllist[i].cell_type=='code'){
            if (celllist[i].metadata.JPSL.hide_code_on_print==true){
                celllist[i].input[0].classList.remove("hidden");
            }
        }
    }
};

/*
input/textarea utilities
*/

JPSLUtils.record_input = function (element){
    var nodetype = element.nodeName.toLowerCase();
    var tempval = ''+element.value;//force to string
    var tempsize = ''+element.size;
    if (tempsize==null){tempsize='7'};
    var tempclass = element.className;
    if (tempclass==null){tempclass=''};
    var tempid = element.id;
    if (tempid==null){tempid=''};
    var tempelem = document.createElement(nodetype);
    tempelem.className =tempclass;
    tempelem.id=tempid;
    tempelem.setAttribute('size',tempsize);
    if (nodetype=='input'){
        tempelem.setAttribute('value',tempval);
    } else {
        tempelem.innerHTML = element.value;
    }
    tempelem.setAttribute('onblur','JPSLUtils.record_input(this)');
    element.replaceWith(tempelem);
};

/*
Python Execution
*/
JPSLUtils.wait_for_python = function(cmdstr){
    return new Promise((resolve,reject) => {
        var callbacks = {
            iopub: {
                output: (data) => resolve(data.content.text.trim())
            },

            shell: {
                reply: (data) => resolve(data.content.status)
            }

        };
        Jupyter.notebook.kernel.execute(cmdstr, callbacks);
    });
}

JPSLUtils.executePython = function(python) {
    return new Promise((resolve, reject) => {
        var callbacks = {
            iopub: {
                output: (data) => resolve(data.content.text.trim())
            }
        };
        Jupyter.notebook.kernel.execute(`print(${python})`, callbacks);
    });
};

JPSLUtils.executePython2 = function(python) {
    return new Promise((resolve, reject) => {
        var callbacks = {
            iopub: {
                output: (data) => resolve(JSON.stringify(data, null, 4))
            }
        };
        Jupyter.notebook.kernel.execute(`print(${python})`, callbacks);
    });
};

/*
Dialogs
*/

JPSLUtils.record_names = function(){
    var currentcell = Jupyter.notebook.get_selected_cell();
    var dlg = document.createElement('div');
    dlg.setAttribute('id','get_names_dlg');
    var tmp = document.createElement('H4');
    var inststr = "In the box below type your name and your partners' names";
    inststr += " (one per line):";
    tmp.innerHTML=inststr;
    dlg.append(tmp);
    tmp = document.createElement('div');
    tmp.innerHTML = '<textarea cols="30" onblur="JPSLUtils.record_input(this)"/>';
    dlg.append(tmp);
    $(dlg).dialog({modal:true,
                  classes:{'ui-dialog-titlebar-close' : 'hidden'
                  },
                  buttons:[
                  {text: 'OK/Do It',
                  click: function(){var rcrd = document.getElementById(
                                    'Last-User');
                                    var parent = rcrd.parentNode;
                                    var dlg = document.getElementById(
                                    'get_names_dlg');
                                    var textboxes = dlg.querySelectorAll(
                                    "textarea");
                                    var tmp = document.createElement('div');
                                    tmp.setAttribute('id','Grp-names');
                                    tmp.
                                    setAttribute('style','font-weight:bold;');
                                    var refeed = /\r?\n|\n\r?|\n/g;
                                    var tmpstr = 'Partners: '+ textboxes[0]
                                    .innerHTML.replace(refeed,'; ');
                                    //tmpstr.replace(refeed,'; ');
                                    tmp.innerHTML = tmpstr;
                                    tmpstr = '# '+rcrd.innerHTML.replaceAll
                                    ('|','\n# ') +'\n#  '+tmpstr;
                                    //rcrd.append(tmp);
                                    JPSLUtils.
                                    insert_newline_at_end_of_current_cell(
                                    tmpstr);
                                   $(this).dialog('destroy');}}
                  ]})
    Jupyter.notebook.focus_cell();//Make sure keyboard manager doesn't grab inputs.
    Jupyter.notebook.keyboard_manager.enabled=false;
    dlg.focus();
    Jupyter.notebook.keyboard_manager.enabled=false; //Make sure keyboard manager doesn't grab inputs.
};

/*
JPSL Tools Menu
*/
JPSLUtils.createJPSLToolsMenu = function(){
    if(!document.getElementById('JPSL_Tools')){
        var hidecells = {'type':'action',
                            'title':'Hide Cells',
                            'data':"JPSLUtils.hide_hide_on_print_cells();"
                          };
        var showcells = {'type':'action',
                            'title':'Undo Hide Cells',
                            'data':"JPSLUtils.show_hide_on_print_cells();"
                          };
        var showtablecode = {'type':'action',
                            'title':'Show Table Creation Code',
                            'data':"JPSLUtils.show_input_table_code();"
                          };
        var hidetablecode = {'type':'action',
                            'title':'Hide Table Creation Code',
                            'data':"JPSLUtils.hide_input_table_code();"
                          };
        var showcode = {'type':'action',
                            'title':'Show Hidden Code',
                            'data':"JPSLUtils.show_hide_code_code();"
                          };
        var hidecode = {'type':'action',
                            'title':'Re-Hide Hidden Code',
                            'data':"JPSLUtils.hide_hide_code_code();"
                          };
        var initJupyterPiDAQ = {'type':'snippet',
                                'title':'Initialize JupyterPiDAQ',
                                'data':["from jupyterpidaq.DAQinstance import *"]
                                };
        var JupyterPiDAQdocs = {'type':'url',
                                'title':'Documentation',
                                'data':"https://jupyterphysscilab.github.io/JupyterPiDAQ/"
                                };
        var PiDAQsubmn = {'type':'submenu',
                         'title':"JupyterPiDAQ",
                         'data':[initJupyterPiDAQ, JupyterPiDAQdocs]
                         };
        var initalgwsymp = {'type':'snippet',
                            'title':'Initialize Algebra with Sympy',
                            'data':["from algebra_with_sympy import *"]
                            };
        var algwsymdocs = {'type':'url',
                           'title':'Documentation',
                           'data':"https://gutow.github.io/Algebra_with_Sympy/"
                           };
        var algwsymsubmn = {'type':'submenu',
                         'title':"Algebra with Sympy",
                         'data':[initalgwsymp, algwsymdocs]
                         };
        var initpandasGUI = {'type':'snippet',
                            'title':'Initialize GUI',
                            'data':["from pandas_GUI import *"]
                            };
        var pandasGUIdocs = {'type':'url',
                           'title':'Documentation',
                           'data':"https://jupyterphysscilab.github.io/jupyter_Pandas_GUI/"
                           };
        var newcolGUI = {'type':'snippet',
                            'title':'New Calculated Column GUI',
                            'data':["new_pandas_column_GUI()"]
                            };
        var plotGUI = {'type':'snippet',
                            'title':'Plot Pandas Data GUI',
                            'data':["plot_pandas_GUI()"]
                            };
        var fitGUI = {'type':'snippet',
                            'title':'Fit Pandas Data GUI',
                            'data':["fit_pandas_GUI()"]
                            };
        var pandasGUIsubmn = {'type':'submenu',
                         'title':"Jupyter Pandas GUI",
                         'data':[initpandasGUI, pandasGUIdocs, newcolGUI,
                         plotGUI, fitGUI]
                         };
        var menu = {'type':'menu',
                    'title':'JPSL Tools',
                    'data':[hidecells, showcells, showtablecode, hidetablecode,
                     showcode, hidecode, algwsymsubmn, PiDAQsubmn, pandasGUIsubmn
                    ]
                    };
        JPSLMenus.build(menu);
    }
};

JPSLUtils.getenv();