		$(function(){

			// Tabs
			$('#tabs').tabs();
			$('#tabsOut').tabs();
			
			// menu superfish
			$('#navigationTop').superfish();
			
			// Dialog			
			$('#dialog_ignore').dialog({
				autoOpen: false,
				width: 600,
				modal: true,
				buttons: {
					"Ok": function() { 
						$('#form_action').submit();
						$(this).dialog("close"); 
					}, 
					"Cancel": function() { 
						$(this).dialog("close"); 
					} 
				}
			});
			
			// Dialog Link
			$('#ignore').click(function(){
				$("#form_action").validate();
				$('#dialog_ignore').dialog('open');
				return false;
			});
			// dataTable
			var uTable = $('#example').dataTable( {
				"sScrollY": 200,
				"bJQueryUI": true,
				"sPaginationType": "full_numbers"
			} );
			$(window).bind('resize', function () {
				uTable.fnAdjustColumnSizing();
			} );
			
		});
		
		function submitFunction(url) {

			document.form_action.action=url;
			$("#form_action").validate();
			$("#form_action").submit();
		}
		
		$(document).ready(function(){
		        
		        $("#toggle").hover(function(){
		        	$("#toggle_div").show();
		        	})	     
		        
		         $("#form_action").validate({
			        rules: {
		        	    comment: "required",
		                category: "required",
			        },
			        messages: {
			            comment: "Please leave a message.",
			            category: "Please choose an option",				
			        },
			        errorClass: "error",
			        validClass: "valid"			       
			    })
		        
		        
		        $("#toggle_div").mouseleave(function(){
		        	$("#toggle_div").slideToggle();
		        	})
		    });	