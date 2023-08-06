window.addEventListener("load",function(){
    regex_area = document.getElementById("regex_input")
    text_area = document.getElementById("text_input")
    text_area.addEventListener("input", function(){
        text_area = document.getElementById("text_input")
        customArea = document.getElementById("front")
        customArea.innerHTML = text_area.value.replaceAll('\n' ,'<br>');
    });
    regex_area.addEventListener("input", function(){
         if (regex_area.value == ""){
            customArea.innerHTML = text_area.value.replaceAll('\n' ,'<br>');
            return 
         }
         customArea.innerHTML = text_area.value.replaceAll('\n' ,'<br>');
         var re = new RegExp("("+ regex_area.value+ ")",flag="g");
         text_area = document.getElementById("text_input")
         customArea.innerHTML = customArea.innerHTML.replace(re,"<span class='blue'>$1</span>")
     });
 });


 String.prototype.replaceAt = function(index, replacement) {
    return this.substring(0, index) + replacement + this.substring(index + this.length);
}