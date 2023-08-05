window.onload = function(){
    const select_tipo_conteudo_custom = document.querySelector('select#id_local');
    console.log(select_tipo_conteudo_custom);
    if(select_tipo_conteudo_custom.value && select_tipo_conteudo_custom.value == 'Geral - Site'){

        // Mostrar Campos do Geral
        document.querySelector('.field-possui_troca_senha').style.display = "block";
        document.querySelector('.field-possui_cadastro').style.display = "block";
        document.querySelector('.field-logo').style.display = "block";

        // Esconder Campos individuais
        document.querySelector('.field-titulo').style.display = "none";

    }else{

        // Mostrar Campos do Individual
        document.querySelector('.field-titulo').style.display = "block";

        // Esconder Campos do Geral
        document.querySelector('.field-possui_troca_senha').style.display = "none";
        document.querySelector('.field-possui_cadastro').style.display = "none";
        document.querySelector('.field-logo').style.display = "none";

    }
    
    select_tipo_conteudo_custom.addEventListener('change', (event) => {
        if(select_tipo_conteudo_custom.value && select_tipo_conteudo_custom.value == 'Geral - Site'){

        // Mostrar Campos do Geral
            document.querySelector('.field-possui_troca_senha').style.display = "block";
            document.querySelector('.field-possui_cadastro').style.display = "block";
            document.querySelector('.field-logo').style.display = "block";

        // Esconder Campos do individual
            document.querySelector('.field-titulo').style.display = "none";

        }else{

        // Mostrar Campos do Individual
            document.querySelector('.field-titulo').style.display = "block";

        // Esconder Campos do Geral
            document.querySelector('.field-possui_troca_senha').style.display = "none";
            document.querySelector('.field-possui_cadastro').style.display = "none";
            document.querySelector('.field-logo').style.display = "none";
            
        }
      });
}


