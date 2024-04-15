var next_click=document.querySelectorAll(".next_button");
var main_form=document.querySelectorAll(".main");
var step_list = document.querySelectorAll(".progress-bar-cus li");
var num = document.querySelector(".step-number");
let formnumber=0;

next_click.forEach(function(next_click_form){
    next_click_form.addEventListener('click',function(){
        if(!validateForm1()){
            return false
        }
       formnumber++;
       updateform();
       progress_forward();
       contentchange();
    });
});

var back_click=document.querySelectorAll(".back_button");
back_click.forEach(function(back_click_form){
    back_click_form.addEventListener('click',function(){
       formnumber--;
       updateform();
       progress_backward();
       contentchange();
    });
});

var username=document.querySelector("#user_name");
var shownname=document.querySelector(".shown_name");


var submit_click=document.querySelectorAll(".submit_button");
submit_click.forEach(function(submit_click_form){
    submit_click_form.addEventListener('click',function(){
       shownname.innerHTML= username.value;
       formnumber++;
       updateform();
    });
});

var carrierForm=document.querySelector("#registerCarrier");
if(carrierForm!=undefined){
carrierForm.addEventListener('submit', function(event) {
    // Prevent the form from submitting
    event.preventDefault();

    // Your custom validation function
    if (validateForm1()) {
        // If validation passes, you can submit the form programmatically
        this.submit();
    } else {
        // Handle validation error, show messages, etc.
        alert('Form validation failed. Please check your inputs.');
    }
});
}


var registerShipper=document.querySelector("#registerShipper");
if(registerShipper!=undefined){
registerShipper.addEventListener('submit', function(event) {
    // Prevent the form from submitting
    event.preventDefault();

    // Your custom validation function
    if (validateForm1()) {
        // If validation passes, you can submit the form programmatically
        this.submit();
    } else {
        // Handle validation error, show messages, etc.
        alert('Form validation failed. Please check your inputs.');
    }
});
}

var registerIndShipper=document.querySelector("#registerIndShipper");
if(registerIndShipper!=undefined){
registerIndShipper.addEventListener('submit', function(event) {
    // Prevent the form from submitting
    event.preventDefault();

    // Your custom validation function
    if (validateForm1()) {
        // If validation passes, you can submit the form programmatically
        this.submit();
    } else {
        // Handle validation error, show messages, etc.
        alert('Form validation failed. Please check your inputs.');
    }
});
}

let optionSelected ="";

var selectButton=document.querySelectorAll(".select-btn")
selectButton.forEach(function(selectButtonClick){
selectButtonClick.addEventListener('click',function(){
      // Remove 'active' class from all buttons
      debugger;
      $(".select-btn").removeClass('btn-primary');
      $(".select-btn").removeClass('active');

      // Add 'active' class to the clicked button
      $(this).addClass('active');
      optionSelected = $(this).attr('id');
      $(this).addClass('btn-primary');


    });
    });

$("#proceed").click(function(){
    if(optionSelected==""){
       alert('Please select one option;')
       return;
    }
    else{
     $("#selection").removeClass('active');
     debugger;
    if(optionSelected=="individual")
            $("#shipperIndividual").addClass('active');

    else if(optionSelected=="business"){
     $("#shipperBusiness").addClass('active');
        }

       formnumber++;
       progress_forward();
       contentchange();
     }

});


function updateform(){
    main_form.forEach(function(mainform_number){
        mainform_number.classList.remove('active');
    })
    main_form[formnumber].classList.add('active');
}

function progress_forward(){
    // step_list.forEach(list => {

    //     list.classList.remove('active');

    // });


    num.innerHTML = formnumber+1;
    step_list[formnumber].classList.add('active');
}

function progress_backward(){
    var form_num = formnumber+1;
    step_list[form_num].classList.remove('active');
    num.innerHTML = form_num;
}

var step_num_content=document.querySelectorAll(".step-number-content");

 function contentchange(){
     step_num_content.forEach(function(content){
        content.classList.remove('active');
        content.classList.add('d-none');
     });
     step_num_content[formnumber].classList.add('active');
 }




function validateform(){
    validate=true;
    var validate_inputs=document.querySelectorAll(".main.active input");
    validate_inputs.forEach(function(vaildate_input){
        vaildate_input.classList.remove('warning');
        if(vaildate_input.hasAttribute('require')){
            if(vaildate_input.value.length==0){
                validate=false;
                vaildate_input.classList.add('warning');
            }
        }
    });
    return validate;

}


function validateForm1()
{
var allFieldsValid = true;
 var validate_inputs=document.querySelectorAll(".main.active input");
    validate_inputs.forEach(function(input) {
        // Check if the field is empty
        if (input.value.trim() === '') {
            allFieldsValid = false;
            // Optionally, you can highlight the invalid field or display an error message.
            // For example, you can add a red border to the invalid field:
            input.style.border = '1px solid red';
        }
    });

             return allFieldsValid;
}

