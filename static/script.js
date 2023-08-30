document.addEventListener("DOMContentLoaded",function(){
  // $('.count').each(function () {
  //   $(this).prop('Counter',0).animate({
  //       Counter: $(this).text()
  //   }, {
  //       duration: 1500,
  //       easing: 'linear',
  //       step: function (now) {
  //           $(this).text(Math.ceil(now));
  //       }
  //   });
  // });
//   $('.count').each(function () {
//     const finalValue = parseInt($(this).text()); // Get the final counter value
//     const progressCircle = $(this).siblings('.progress-circle');

//     $(this).prop('Counter', 0).animate({
//         Counter: finalValue
//     }, {
//         duration: 1500,
//         easing: 'linear',
//         step: function (now) {
//             $(this).text(Math.ceil(now)); // Update the numbers
            
//             // Calculate the percentage completion
//             const percentage = (now / finalValue) * 100;
            
//             // Update the progress circle color and rotation based on the percentage
//             progressCircle.css('transform', `rotate(${percentage * 3.6}deg)`); // Each percentage point is 3.6 degrees
//             progressCircle.css('border-top-color', `rgb(${255 - percentage * 2.55}, ${percentage * 2.55}, 0)`); // Red to Green color transition
//         },
//         complete: function() {
//             progressCircle.css('border-top-color', 'green'); // Ensure the circle is fully green at completion
//         }
//     });
// });
  function animateCounterText($element, finalValue) {
    $element.prop('Counter', 0).animate({
        Counter: finalValue
    }, {
        duration: 5000,
        easing: 'linear',
        step: function (now) {
            $element.text(Math.ceil(now));
        }
    });
  }
  function animateCounterCircle($element, finalValue) {
    $element.prop('Counter', 0).animate({
        Counter: finalValue
    }, {
        duration: 5000,
        easing: 'linear',
        step: function (now) {
            $element.text(Math.ceil(now));
        }
    });
  }
  let circularProgress = document.querySelector(".progress-text"),
      circularProgress1 = document.querySelector(".progress-text1"),
      circularProgress2 = document.querySelector(".progress-text2"),
      circularProgress3 = document.querySelector(".progress-text3"),
      progressValue = document.querySelector(".count"),
      progressValue1 = document.querySelector(".count1"),
      progressValue2 = document.querySelector(".count2"),
      progressValue3 = document.querySelector(".count3");
  let progressStartValue = 0,
      progressEndValue = progressValue.textContent,
      progressEndValue1 = progressValue1.textContent,
      progressEndValue2 = progressValue2.textContent,
      progressEndValue3 = progressValue3.textContent,
      speed = 40;
  let progress = setInterval(() => {
      progressStartValue++
      circularProgress.style.background = `conic-gradient(#2D5F00 ${progressStartValue * 3}deg, #fff 0deg)`
      circularProgress1.style.background = `conic-gradient(#2D5F00 ${progressStartValue * 3}deg, #fff 0deg)`
      circularProgress2.style.background = `conic-gradient(#2D5F00 ${progressStartValue * 3}deg, #fff 0deg)`
      circularProgress3.style.background = `conic-gradient(#2D5F00 ${progressStartValue * 3}deg, #fff 0deg)`
      if(progressStartValue == progressEndValue3){
        clearInterval(progress)
      }
  }, speed)

  $('.count').each(function () {
    const $countElement = $(this);
    const finalValue = parseInt($countElement.text());
    
    animateCounterText($countElement, finalValue);
    
  });
  $('.count1').each(function () {
    const $countElement = $(this);
    const finalValue = parseInt($countElement.text());
    
    animateCounterText($countElement, finalValue);
    
  });
  $('.count2').each(function () {
    const $countElement = $(this);
    const finalValue = parseInt($countElement.text());
    
    animateCounterText($countElement, finalValue);
    
  });
  $('.count3').each(function () {
    const $countElement = $(this);
    const finalValue = parseInt($countElement.text());
    
    animateCounterText($countElement, finalValue);
    
  });


  var loc = window.location.pathname
  console.log(loc)
  abt = document.getElementById("abt")
  srvs = document.getElementById("srvs")
  cnt = document.getElementById("cnt")
  blg = document.getElementById("blg")
  if(loc=="/about"){
    abt.classList.add('active')
  }else if(loc=="/services"){
    srvs.classList.add('active')
  }else if(loc=="/contact"){
    cnt.classList.add('active')
  }else if(loc=="/blogs"){
    blg.classList.add('active')
  }

  $(document).ready(function() {
    $('input#input_text, textarea#textarea2').characterCounter();
  });

  var dropdownElems = document.querySelectorAll('.dropdown-trigger');
    var options = {
      constrainWidth: false,
      coverTrigger: false,
      alignment: 'right'
    };
  M.Dropdown.init(dropdownElems, options);


})


  // JavaScript code for hiding the WhatsApp widget on scroll down
  const whatsappWidget = document.querySelector('.whatsapp-widget');
  let lastScrollPosition = window.scrollY;

  window.addEventListener('scroll', () => {
    const currentScrollPosition = window.scrollY;
    if (currentScrollPosition > lastScrollPosition) {
      // whatsappWidget.style.opacity = '0';
    } else {
      // whatsappWidget.style.opacity = '1';
    }
    lastScrollPosition = currentScrollPosition;
  });
  
  function toggle(btn,text){
    console.log(btn)
    console.log(text)
    const passwordInput1 = document.getElementById(text);
    const pviewIcon1 = document.getElementById(btn);
  
    if (passwordInput1.type === "password") {
      passwordInput1.type = "text";
      pviewIcon1.textContent = "visibility";
    } else {
      passwordInput1.type = "password";
      pviewIcon1.textContent = "visibility_off";
    }
  
  }

  function execCmd(command, value = null) {
    document.execCommand(command, false, value);
  }
  tinymce.init({
    selector: "#myTextarea",
    plugins: "mentions anchor autolink charmap codesample emoticons image link lists media searchreplace table visualblocks wordcount checklist mediaembed casechange export formatpainter pageembed permanentpen footnotes advtemplate advtable advcode editimage tableofcontents mergetags powerpaste tinymcespellchecker autocorrect a11ychecker typography inlinecss",
    toolbar: "undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table mergetags | align lineheight | tinycomments | checklist numlist bullist indent outdent | emoticons charmap | removeformat",
    image_title: true,
    images_upload_url: '/upload_image', // Flask endpoint for image upload
    automatic_uploads: true,
    images_reuse_filename: true,
    convert_urls: false,
    // images_upload_handler: function (blobInfo, success, failure) {
    //   var xhr, formData;
    //   xhr = new XMLHttpRequest();
    //   xhr.withCredentials = false;
    //   xhr.open('POST', '/upload_image', true);  // Your upload endpoint
    //   xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");

    //   xhr.onload = function () {
    //     if (xhr.status === 200) {
    //         var response = JSON.parse(xhr.responseText);
    //         if (response.location) {
    //             success(response.location);
    //         } else {
    //             failure('Invalid response from server');
    //         }
    //     } else {
    //         failure('HTTP Error: ' + xhr.status);
    //     }
    //   };

    //   formData = new FormData();
    //   formData.append('file', blobInfo.blob(), blobInfo.filename());

    //   xhr.send(formData);
    // },
  
    setup: function (editor) {
      editor.on('change', function () {
        // Handle the content change here
        console.log('Content changed:', editor.getContent());
      });
    }
  });