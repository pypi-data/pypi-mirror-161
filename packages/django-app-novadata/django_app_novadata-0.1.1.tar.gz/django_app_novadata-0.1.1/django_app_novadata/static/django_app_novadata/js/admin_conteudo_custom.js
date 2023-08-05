window.onload = function(){
    const select_tipo_conteudo_custom = document.querySelector('select#id_local');
    console.log(select_tipo_conteudo_custom);
    if(select_tipo_conteudo_custom.value && select_tipo_conteudo_custom.value == 'Logo - Admin'){
        document.querySelector('.field-logo').style.display = "block";
        document.querySelector('.field-conteudo').style.display = "none";
    }else{
        document.querySelector('.field-conteudo').style.display = "block";
        document.querySelector('.field-logo').style.display = "none";
    }
    select_tipo_conteudo_custom.addEventListener('change', (event) => {
        if(select_tipo_conteudo_custom.value && select_tipo_conteudo_custom.value == 'Logo - Admin'){
            document.querySelector('.field-logo').style.display = "block";
            document.querySelector('.field-conteudo').style.display = "none";
        }else{
            document.querySelector('.field-conteudo').style.display = "block";
            document.querySelector('.field-logo').style.display = "none";
        }
      });
}


