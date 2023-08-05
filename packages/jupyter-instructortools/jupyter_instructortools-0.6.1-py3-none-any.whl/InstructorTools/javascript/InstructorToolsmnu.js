let InstructorTools = new Object();

InstructorTools.createInstructorToolsMenu = function(){
    var donotinstall = Jupyter.notebook.metadata.noinstructortool;
    if (donotinstall){
        alert('Installation of Instructor Tools is forbidden in this '+
        'notebook!');
        InstructorTools.deleteInstructorToolsMenuPerm();
        return;
    }
    if(!document.getElementById('Instructor_Tools')){
        var newDataTable = {'type':'action',
                            'title': 'Insert Data Entry Table...',
                            'data':"get_table_dim();"
                            };
        var grnstart = {'type':'snippet',
                        'title':'Insert green start bar',
                        'data':["<div style = \"width: 100%; height:10px;"+
                        "border-width:5px; border-color:green;" +
                        "border-style:solid;border-bottom-style:none;" +
                        "margin-bottom: 4px; min-width: 15px;" +
                        "background-color:yellow;\"></div>\n\n"]
                        };
        var brnstop = {'type':'snippet',
                        'title':'Insert brown stop bar',
                        'data':["\n<div style = \"width: 100%; height:10px;" +
                        "border-width:5px;border-color:sienna;" +
                        "border-style:solid;border-top-style:none;" +
                        "margin-top: 4px; min-width: 15px;" +
                        "background-color:yellow;\"></div>"]
                        };
        var cyanhighlight = {'type':'snippet',
                        'title':'Insert left cyan highlight',
                        'data':["<div style = \"height: 100%; width:10px;" +
                        "float:left; border-width:5px; border-color:cyan;" +
                        "border-style:solid; border-right-style:none;" +
                        "margin-right: 4px; min-height: 15px;\"></div>\n\n"]
                        };
        var redhighlight = {'type':'snippet',
                        'title':'Insert left red highlight',
                        'data':["<div style = \"height: 100%; width:10px;" +
                        "float:left; border-width:5px; border-color:red;" +
                        "border-style:solid; border-right-style:none;" +
                        "margin-right: 4px; min-height: 15px;\"></div>\n\n"]
                        };
        var protectcells = {'type':'action',
                            'title': 'Protect Selected Cells',
                            'data':"InstructorTools.protect_selected_cells();"
                            };
        var deprotectcells = {'type':'action',
                            'title': 'Deprotect Selected Cells',
                            'data':"InstructorTools.deprotect_selected_cells();"
                            };
        var indicateprotectcells = {'type':'action',
                            'title': 'Indicate Protected Cells',
                            'data':"InstructorTools.mark_protected_cells();"
                            };
        var allowhiding = {'type':'action',
                            'title': 'Allow Hiding Selected Cells',
                            'data':"InstructorTools.set_hide_selected_cells_on_print();"
                            };
        var unsethiding = {'type':'action',
                            'title': 'Disallow Hiding Selected Cells',
                            'data':"InstructorTools.unset_hide_selected_cells_on_print();"
                            };
        var indicateallowhiding = {'type':'action',
                            'title': 'Indicate Cells Allowed to Hide',
                            'data':"InstructorTools.mark_hide_on_print_cells();"
                            };
        var setallowhidecode = {'type':'action',
                            'title': 'Allow Hiding Selected Code',
                            'data':"InstructorTools.set_hide_code_on_print();"
                            };
        var unsetallowhidecode = {'type':'action',
                            'title': 'Disallow Hiding Selected Code',
                            'data':"InstructorTools.unset_hide_code_on_print();"
                            };
        var indicateallowhidecode = {'type':'action',
                            'title': 'Indicate Code Allowed to Hide',
                            'data':"InstructorTools.mark_hide_code_on_print_cells();"
                            };
        var tsthideonprint = {'type':'action',
                            'title': 'Test Hide on Print',
                            'data':"JPSLUtils.hide_hide_on_print_cells();"
                            };
        var showhideonprint = {'type':'action',
                            'title': 'Undo Hide on Print',
                            'data':"JPSLUtils.show_hide_on_print_cells();"
                            };
        var sethidecodeJPSL = {'type':'action',
                            'title': 'Set Hide Code in JPSL',
                            'data':"InstructorTools.set_hide_code();"
                            };
        var unsethidecodeJPSL = {'type':'action',
                            'title': 'Unset Hide Code in JPSL',
                            'data':"InstructorTools.unset_hide_code();"
                            };
        var indicatehidecodeJPSL = {'type':'action',
                            'title': 'Indicate Hide Code in JPSL',
                            'data':"InstructorTools.mark_hide_code_cells();"
                            };
        var timestampnames = {'type':'snippet',
                            'title': 'Insert get names and timestamp',
                            'data':["import JPSLUtils",
                            "JPSLUtils.JPSL_Tools_Menu()",
                            "JPSLUtils.record_names_timestamp()"]
                            };
        var deactivatemenu = {'type':'action',
                            'title': 'Deactivate this menu',
                            'data':"InstructorTools.deleteInstructorToolsMenu();"
                            };
        var deactivatemenuperm = {'type':'action',
                            'title': '!deactivate permanently!',
                            'data':"InstructorTools.deleteInstructorToolsMenuPerm();"
                            };
        var initboilerplate = {'type':'computedsnippet',
                        'title':'Insert initialization boilerplate',
                        'data':"InstructorTools.insert_init_boilerplate()"
                        };
        var protectsubmnu = {'type':'submenu',
                    'title':'Cell Locking',
                    'data':[protectcells, deprotectcells, indicateprotectcells]
                    };
        var mkdownsubmnu = {'type':'submenu',
                    'title':'Markdown Cell Highlighting',
                    'data':[cyanhighlight, redhighlight, grnstart, brnstop]
                    };
        var hideonprintsubmnu = {'type':'submenu',
                    'title':'Hide on Print',
                    'data':[allowhiding, unsethiding, indicateallowhiding,
                    tsthideonprint, showhideonprint,
                    setallowhidecode, unsetallowhidecode, indicateallowhidecode]
                    };
        var JPSLhidesubmnu = {'type':'submenu',
                    'title':'Hide Code in JPSL',
                    'data':[sethidecodeJPSL, unsethidecodeJPSL,
                    indicatehidecodeJPSL]
                    };
        var mnuctl = {'type':'submenu',
                    'title':'Menu Control',
                    'data':[deactivatemenu, deactivatemenuperm]
                    };
        var menu = {'type':'menu',
                    'title':'Instructor Tools',
                    'data':[timestampnames, initboilerplate, newDataTable,
                    mkdownsubmnu, hideonprintsubmnu, JPSLhidesubmnu,
                    protectsubmnu, mnuctl]
                    };
        JPSLMenus.build(menu);
    }
}

InstructorTools.deleteInstructorToolsMenu = function(){
    if(document.getElementById('Instructor_Tools')){
        document.getElementById('Instructor_Tools').remove();
    }
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        var should_delete = false;
        if(celllist[i].get_text().indexOf('from InstructorTools import *') !== -1){
            should_delete = true
        }
        if (celllist[i].get_text().indexOf('import InstructorTools')!== -1){
            should_delete = true
        }
        if(celllist[i].get_text().indexOf('instmenu_act()') !== -1){
            should_delete = true
        }
        if (should_delete){
            //delete the cell
            var cellindex=Jupyter.notebook.find_cell_index(celllist[i]);
            //alert('cellindex: '+cellindex)
            Jupyter.notebook.delete_cell(cellindex);
        }
    }
}
InstructorTools.deleteInstructorToolsMenuPerm = function(){
    if(document.getElementById('Instructor_Tools')){
        document.getElementById('Instructor_Tools').remove();
    }
    Jupyter.notebook.metadata.noinstructortool=true;
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        var should_delete = false;
        if(celllist[i].get_text().indexOf('from InstructorTools import *') !== -1){
            should_delete = true
        }
        if (celllist[i].get_text().indexOf('import InstructorTools')!== -1){
            should_delete = true
        }
        if(celllist[i].get_text().indexOf('instmenu_act()') !== -1){
            should_delete = true
        }
        if (should_delete){
            //delete the cell
            var cellindex=Jupyter.notebook.find_cell_index(celllist[i]);
            //alert('cellindex: '+cellindex)
            Jupyter.notebook.delete_cell(cellindex);
        }
    }

}

InstructorTools.protect_selected_cells = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        celllist[i].metadata.editable=false;
        celllist[i].element.children()[0].setAttribute("style","background-color:pink;");
        }
}

InstructorTools.deprotect_selected_cells = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        celllist[i].metadata.editable=true;
        celllist[i].element.children()[0].removeAttribute("style");
    }
}

InstructorTools.mark_protected_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.editable==false){
        celllist[i].element.children()[0].setAttribute("style","background-color:pink;");
        } else {
        celllist[i].element.children()[0].removeAttribute("style");
        }
    }
}

InstructorTools.set_hide_selected_cells_on_print = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        if (!celllist[i].metadata.JPSL){
        celllist[i].metadata.JPSL={}}
        celllist[i].metadata.JPSL.hide_on_print=true;
        celllist[i].element.children()[0].setAttribute("style",
        "background-color:magenta;");
        }
}

InstructorTools.unset_hide_selected_cells_on_print = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        if (!celllist[i].metadata.JPSL){
        celllist[i].metadata.JPSL={}}
        celllist[i].metadata.JPSL.hide_on_print=false;
        celllist[i].element.children()[0].removeAttribute("style");
    }
}

InstructorTools.mark_hide_on_print_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL){
            if (celllist[i].metadata.JPSL.hide_on_print==true){
                celllist[i].element.children()[0].setAttribute("style",
                "background-color:magenta;");
                } else {
                celllist[i].element.children()[0].removeAttribute("style");
            }
        }
    }
}

InstructorTools.set_hide_code_on_print = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        if (!celllist[i].metadata.JPSL){
        celllist[i].metadata.JPSL={}}
        celllist[i].metadata.JPSL.hide_code_on_print=true;
        celllist[i].element.children()[0].setAttribute("style",
        "background-color:orange;");
        }
}

InstructorTools.unset_hide_code_on_print = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        if (!celllist[i].metadata.JPSL){
        celllist[i].metadata.JPSL={}}
        celllist[i].metadata.JPSL.hide_code_on_print=false;
        celllist[i].element.children()[0].removeAttribute("style");
        }
}

InstructorTools.mark_hide_code_on_print_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL){
            if (celllist[i].metadata.JPSL.hide_code_on_print==true){
                celllist[i].element.children()[0].setAttribute("style",
                "background-color:orange;");
                } else {
                celllist[i].element.children()[0].removeAttribute("style");
            }
        }
    }
}

InstructorTools.set_hide_code = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        if (!celllist[i].metadata.JPSL){
        celllist[i].metadata.JPSL={}}
        celllist[i].metadata.JPSL.hide_code=true;
        celllist[i].element.children()[0].setAttribute("style",
        "background-color:yellow;");
        }
}

InstructorTools.unset_hide_code = function(){
    var celllist = Jupyter.notebook.get_selected_cells();
    for (var i = 0;i<celllist.length;i++){
        if (!celllist[i].metadata.JPSL){
        celllist[i].metadata.JPSL={}}
        celllist[i].metadata.JPSL.hide_code=false;
        celllist[i].element.children()[0].removeAttribute("style");
        }
}

InstructorTools.mark_hide_code_cells = function(){
    var celllist = Jupyter.notebook.get_cells();
    for (var i = 0;i<celllist.length;i++){
        if (celllist[i].metadata.JPSL){
            if (celllist[i].metadata.JPSL.hide_code==true){
                celllist[i].element.children()[0].setAttribute("style",
                "background-color:yellow;");
                } else {
                celllist[i].element.children()[0].removeAttribute("style");
            }
        }
    }
}

InstructorTools.insert_init_boilerplate = function(){
    var mkdstr = "### You must initialize the software each time you use \
    this notebook.\n";
    mkdstr += " 1. First, check that the notebook is \"Trusted\" by looking \
    near";
    mkdstr += " the right of the Jupyter toolbars. If the notebook is not \
    trusted";
    mkdstr += " you need to click on the \"not trusted\" button and trust the";
    mkdstr += " notebook. **You should only trust notebooks that come from a";
    mkdstr += " *trusted source*, such as the class website.**\n";
    mkdstr += " 2. The cell immediately below contains code that loads the";
    mkdstr += " software modules necessary for this notebook to run. It also";
    mkdstr += " collects some bookkeeping information that can be used for";
    mkdstr += " troubleshooting. **You must run this cell each time you open";
    mkdstr += " the notebook or later cells may not work.**\n";
    mkdstr += " 3. If you are doing calculations that depend upon";
    mkdstr += " using variables passed from calculations done the previous";
    mkdstr += " time the notebook was opened, you will need to run those";
    mkdstr += " previous cells to redefine the variables.\n";
    mkdstr += " 4. *DO NOT run cells that contain plot displays of live data";
    mkdstr += " collection, as that will restart the data collection.* You can";
    mkdstr += " reload data collected from the `.csv` files  written for each";
    mkdstr += " collection run. Ideally you would do this in a new notebook.";

    return (mkdstr);
}