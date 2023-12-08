function setEnglishDatepicker() {
    $("#datepicker, #date").datepicker({
        monthNames: ['January','February','March','April','May','June','July','August','September','October','November','December'],
        monthNamesShort: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
        dayNames: ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],
        dayNamesShort: ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],
        dayNamesMin: ['Su','Mo','Tu','We','Th','Fr','Sa'],
        showMonthAfterYear: false,
        yearSuffix: "",
        weekHeader: "W",
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
    });
}
function setGermanDatepicker() {
    $("#datepicker, #date").datepicker({
        monthNames: ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
        monthNamesShort: ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'],
        dayNames: ['Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag'],
        dayNamesShort: ['So','Mo','Di','Mi','Do','Fr','Sa'],
        dayNamesMin: ['So','Mo','Di','Mi','Do','Fr','Sa'],
        showMonthAfterYear: false,
        firstDay: 1,
        yearSuffix: "",
        weekHeader: "W",
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
    });
}
function setFrenchDatepicker() {
    $("#datepicker, #date").datepicker({
        monthNames: ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'],
        monthNamesShort: ['janv.','févr.','mars','avril','mai','juin','juil.','août','sept.','oct.','nov.','déc.'],
        dayNames: ['dimanche','lundi','mardi','mercredi','jeudi','vendredi','samedi'],
        dayNamesShort: ['dim.','lun.','mar.','mer.','jeu.','ven.','sam.'],
        dayNamesMin: ['di','lu','ma','me','je','ve','sa'],
        showMonthAfterYear: false,
        firstDay: 1,
        yearSuffix: "",
        weekHeader: "W",
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
    });
}
function setItalianDatepicker() {
    $("#datepicker, #date").datepicker({
        monthNames: ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'],
        monthNamesShort: ['Gen','Feb','Mar','Apr','Mag','Giu','Lug','Ago','Set','Ott','Nov','Dic'],
        dayNames: ['domenica','lunedì','martedì','mercoledì','giovedì','venerdì','sabato'],
        dayNamesShort: ['dom','lun','mar','mer','gio','ven','sab'],
        dayNamesMin: ['do','lu','ma','me','gi','ve','sa'],
        showMonthAfterYear: false,
        firstDay: 1,
        yearSuffix: "",
        weekHeader: "W",
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
    });
}
function setSpanishDatepicker() {
    $("#datepicker, #date").datepicker({
        monthNames: ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],
        monthNamesShort: ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'],
        dayNames: ['domingo','lunes','martes','miércoles','jueves','viernes','sábado'],
        dayNamesShort: ['dom','lun','mar','mié','jue','vie','sáb'],
        dayNamesMin: ['do','lu','ma','mi','ju','vi','sá'],
        showMonthAfterYear: false,
        firstDay: 1,
        yearSuffix: "",
        weekHeader: "W",
        dateFormat: 'yy-mm-dd',
        changeMonth: true,
        changeYear: true,
    });
}