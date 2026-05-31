function politicas(correo){
//Se desactiva el voicemail
var VMDisabled = `       
echo "Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-VM-Disabled"
Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-VM-Disabled

`;

//Se restringe todas las politicas
var AllDisabled = `       
echo "Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-AllDisabled"
Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-AllDisabled

`;

//Desactiva otra llamada entrante cuando se encuentra en llamada.
var BusyOnBusy = `       
echo "Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-BusyOnBusy"
Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-BusyOnBusy

`;

//Todas las politicas permitidas
var AllEnabled = `       
echo "Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-All-Enabled"
Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName CMW-All-Enabled

`;

var AllowCalling = `
echo "Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName AllowCalling"
Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName AllowCalling
`;

var dialplan =`
echo "Grant-CsTenantDialPlan -Identity ${correo}"
Grant-CsTenantDialPlan -Identity ${correo} -PolicyName ISMYCONNECT
`;

var unanswered =`
echo "Set-CsUserCallingSettings -Identity ${correo}  -IsUnansweredEnabled $true -UnansweredDelay 00:00:20 -UnansweredTargetType Voicemail"
Set-CsUserCallingSettings -Identity ${correo}  -IsUnansweredEnabled $true -UnansweredDelay 00:00:20 -UnansweredTargetType Voicemail
`;

return {
    VMDisabled,
    AllDisabled,
    BusyOnBusy,
    AllEnabled,
    AllowCalling,
    dialplan,
    unanswered
};

}

function mostrarFormularioAlta() {
    var checkbox = document.getElementById('alta');
    var formularioBaja = document.getElementById('formularioBaja');
    var formulario = document.getElementById('formularioAlta');
    var PolicyName = document.getElementById('policyID');
    var formularioAltaBaja = document.getElementById('formularioAltaBaja');
    var opciones = document.getElementById('OpAB');
    var span = document.getElementById('span');
    if (checkbox.checked) {
        formulario.style.display = 'block';
        PolicyName.style.display = 'inline-block';
        formularioBaja.style.display = 'none';
        formularioAltaBaja.style.display = 'none';
        opciones.style.display = 'none';
        span.style.display = 'none';
    } else {
        formulario.style.display = 'none';
        formularioAltaBaja.style.display = 'none';
    }
}

function mostrarFormularioBaja() {
    var checkbox = document.getElementById('baja');
    var formulario = document.getElementById('formularioBaja');
    var PolicyName = document.getElementById('policyID');
    var formularioAlta = document.getElementById('formularioAlta');
    var formularioAltaBaja = document.getElementById('formularioAltaBaja');
    var opciones = document.getElementById('OpAB');
    var span = document.getElementById('span');
    if (checkbox.checked) {
        formulario.style.display = 'block';
        formularioAlta.style.display = 'none';
        formularioAltaBaja.style.display = 'none';
        opciones.style.display = 'none';
        span.style.display = 'none';
        PolicyName.style.display = 'none';

    } else {
        formulario.style.display = 'none';
        formularioAltaBaja.style.display = 'none';
    }
}

function mostrarFormularioAltayBaja() {
    var checkbox = document.getElementById('altaBaja');
    var formularioAlta = document.getElementById('formularioAlta');
    var formularioBaja = document.getElementById('formularioBaja');
    var formularioAltaBaja = document.getElementById('formularioAltaBaja');
    var opciones = document.getElementById('OpAB');
    var PolicyName = document.getElementById('policyID');
    var span = document.getElementById('span');
    if (checkbox.checked) {
        formularioAltaBaja.style.display = 'block';
        opciones.style.display = 'block';
        PolicyName.style.display = 'block';
        span.style.display = 'inline';
        document.getElementById("span").style.boxShadow = "none";
        document.getElementById("span").style.border = "none";
        formularioAlta.style.display = 'none';
        formularioBaja.style.display = 'none';
    } else {
        formularioAltaBaja.style.display = 'block';
        formularioAlta.style.display = 'none';
        formularioBaja.style.display = 'none';
    }
}

function generarArchivoAlta() {
    var checkboxA = document.getElementById('All-Enabled');
    var checkboxW = document.getElementById('VM-Disabled');
    var checkboxD = document.getElementById('AllDisabled');
    var checkboxB = document.getElementById('BusyOnBusy');
    var checkboxP = document.getElementById('dialplan');
    var checkboxAC = document.getElementById('allowcalling');
    var checkbox = document.getElementById('allowcalling');
 
    var nombre = document.getElementById('nombreAlta').value;
        let numberOfFields = fieldSelect.value;
var contenidoMed = '';
var contenidoIni = 
`Start-Transcript -Path $env:USERPROFILE\\Desktop\\Config_IMC_${nombre}.txt
        
Import-Module -Name MicrosoftTeams
Connect-MicrosoftTeams
        
          `;

for (let i = 1; i <= numberOfFields; i++) {
            let correo = document.getElementById('correoAlta' + i).value;
            let extension = document.getElementById('extensionAlta' + i).value;
            let numero = document.getElementById('numLoc').value;


var contenidoMed = contenidoMed +`       
echo "Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $true"
Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $true
    
echo "Set-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumber +${numero};ext=${extension} -PhoneNumberType DirectRouting"
Set-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumber "+${numero};ext=${extension}" -PhoneNumberType DirectRouting
    
echo "Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName ISMYCONNECT"
Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName "ISMYCONNECT"
    
    `;

   /* var contenidoMed = contenidoMed +`       
    echo "Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $true"
    Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $true
    
    echo "Set-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumber +${extension} -PhoneNumberType DirectRouting"
    Set-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumber "+${extension}" -PhoneNumberType DirectRouting
    
    echo "Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName ISMYCONNECT"
    Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName "ISMYCONNECT"
    
    `;
*/



var resultado = politicas(correo);

if (checkboxA.checked || checkboxD.checked || checkboxB.checked || checkboxW.checked || checkboxP.checked || checkboxAC.checked) {
        if(checkboxA.checked){
            contenidoMed = contenidoMed + resultado.AllEnabled;
        }
        if (checkboxD.checked) {
            contenidoMed = contenidoMed + resultado.AllDisabled;
        }
        if (checkboxW.checked) {
            contenidoMed = contenidoMed + resultado.VMDisabled;
        } 
        if (checkboxB.checked) {
            contenidoMed = contenidoMed + resultado.BusyOnBusy;
        } 
        if (checkboxP.checked) {
            contenidoMed = contenidoMed + resultado.dialplan;
        } 
        if (checkboxAC.checked) {
            contenidoMed = contenidoMed + resultado.AllowCalling;
        } 
    }
}

var contenido = contenidoIni +  contenidoMed +
`Stop-Transcript`;


        var blob = new Blob([contenido], { type: 'text/plain' });
        var enlace = document.getElementById('descargaEnlace');
        enlace.href = URL.createObjectURL(blob);
        enlace.download = nombre + '.ps1';
        enlace.style.display = 'block';

        var nombre = document.getElementById('nombreAlta').value = '';
        var correo = document.getElementById('correoAlta').value = '';
        var extension = document.getElementById('extensionAlta').value = '';
    }


function generarArchivoBaja() {

    var nombre = document.getElementById('nombreBaja').value;

  let numberOfFields = fieldSelect.value;
  var contenidoMed = '';
  var contenidoIni = 
`Start-Transcript -Path $env:USERPROFILE\\Desktop\\Config_IMC_${nombre}.txt
          
Import-Module -Name MicrosoftTeams
Connect-MicrosoftTeams
          
            `;
          for (let i = 1; i <= numberOfFields; i++) {
              let correo = document.getElementById('correoBaja' + i).value;
              let extension = document.getElementById('extensionBaja' + i).value;
  
  
  var contenidoMed = contenidoMed +`       
echo "Remove-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumberType DirectRouting -PhoneNumber +${extension}"
Remove-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumberType DirectRouting -PhoneNumber +${extension}
      
echo "Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $false"
Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $false
      
echo "Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName $null"
Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName $null
      
echo "Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName $null"
Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName $null
  
  `;
  var resultado = politicas(correo);
  }
  
  var contenido = contenidoIni +  contenidoMed +
`Stop-Transcript`;
  
        var blob = new Blob([contenido], { type: 'text/plain' });
        var enlace = document.getElementById('descargaEnlace');
        enlace.href = URL.createObjectURL(blob);
        enlace.download = nombre + '.ps1';
        enlace.style.display = 'block';


}

function generarArchivoAltaBaja() {
    var checkboxA = document.getElementById('All-Enabled');
    var checkboxW = document.getElementById('VM-Disabled');
    var checkboxD = document.getElementById('AllDisabled');
    var checkboxB = document.getElementById('BusyOnBusy');
    var checkboxP = document.getElementById('dialplan');
    var checkboxAC = document.getElementById('allowcalling');

    var nombre = document.getElementById('nombreAB').value;
    let numberOfFields = fieldSelect.value;
    let numberOfFieldsB = fieldSelectB.value;
var contenidoAlta = '';
var contenidoBaja = '';
var contenidoIni = 
`Start-Transcript -Path $env:USERPROFILE\\Desktop\\Config_IMC_${nombre}.txt
    
Import-Module -Name MicrosoftTeams
Connect-MicrosoftTeams
    
      `;
    for (let i = 1; i <= numberOfFields; i++) {
        let correo = document.getElementById('correoAltaB' + i).value;
        let extension = document.getElementById('extensionAltaB' + i).value;
        let numero = document.getElementById('numLoc').value;


var contenidoAlta = contenidoAlta +`       
echo "Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $true"
Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $true

echo "Set-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumber +${numero};ext=${extension} -PhoneNumberType DirectRouting"
Set-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumber "+${numero};ext=${extension}" -PhoneNumberType DirectRouting

echo "Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName ISMYCONNECT"
Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName "ISMYCONNECT"

`;
var resultado = politicas(correo);

if (checkboxA.checked || checkboxD.checked || checkboxB.checked || checkboxW.checked || checkboxP.checked || checkboxAC.checked) {
        if(checkboxA.checked){
            contenidoAlta = contenidoAlta + resultado.AllEnabled;
        }
        if (checkboxD.checked) {
            contenidoAlta = contenidoAlta + resultado.AllDisabled;
        } 
        if (checkboxW.checked) {
            contenidoAlta = contenidoAlta + resultado.VMDisabled;
        } 
        if (checkboxB.checked) {
            contenidoAlta = contenidoAlta + resultado.BusyOnBusy;
        } 
        if (checkboxP.checked) {
            contenidoAlta = contenidoAlta + resultado.dialplan;
        } 
        if (checkboxAC.checked) {
            contenidoAlta = contenidoAlta + resultado.AllowCalling;
        } 
    }
}


            for (let i = 1; i <= numberOfFieldsB; i++) {
                let correo = document.getElementById('correoBajaA' + i).value;
                let extension = document.getElementById('extensionBajaA' + i).value;
    
    
contenidoBaja = contenidoBaja +`   

echo "Remove-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumberType DirectRouting -PhoneNumber +${extension}"
Remove-CsPhoneNumberAssignment -Identity ${correo} -PhoneNumberType DirectRouting -PhoneNumber +${extension}
        
echo "Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $false"
Set-CsPhoneNumberAssignment -Identity ${correo} -EnterpriseVoiceEnabled $false
        
echo "Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName $null"
Grant-CsOnlineVoiceRoutingPolicy -Identity ${correo} -PolicyName $null
        
echo "Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName $null"
Grant-CsTeamsCallingPolicy -Identity ${correo} -PolicyName $null
    
`;

    }

    var contenido = contenidoIni +  contenidoBaja + contenidoAlta +
`Stop-Transcript`;
    
          var blob = new Blob([contenido], { type: 'text/plain' });
          var enlace = document.getElementById('descargaEnlace');
          enlace.href = URL.createObjectURL(blob);
          enlace.download = nombre + '.ps1';
          enlace.style.display = 'block';

}


