//Copyright (c) 2011 Crystalline Technologies
//
//  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
//  to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
//  and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
//
//  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
//
//  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
//  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
//  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

(function($){	

	//Main method
	$.fn.json2html = function(JSON, transform, options){	
		
		var JSONObject;

		if( jQuery.type(JSON) === "string" ) JSONObject = jQuery.parseJSON(JSON);
		else JSONObject = JSON;

		if( options != undefined ) $.extend($.json2html.options, options);

		return this.each(function(){
		    if( $.json2html.options.prepend ) $(this).prepend( $.json2html(JSONObject, transform) );
			else $(this).append( $.json2html(JSONObject, transform) );
		});
	
	}

	$.json2html = function(JSON, transform)
	{
		return( $.json2html.transformArray(JSON, transform) );
	}

	//Default Options
	$.json2html.options = 
	{
		'eventData': null,
		'prepend':false
	}

		//Private methods
		$.json2html.transformArray = function(array, transform)
		{
			if(transform == null) return(null);

			var html = $(document.createElement("ul"));

			//Validate that this is actually an array
			if (jQuery.type(array) === "array")
			{
				//Itterrate through the array and append it to the html object
				$(array).each(function() {
								
					//Add all children to the parent object
					$(html).append( $.json2html.transformObject(this, transform) );
				});
			} else if (jQuery.type(array) === "object")
			{
			    return( $.json2html.applyTransform(array, transform) );
			}

			return(html);
		}

		$.json2html.transformObject = function(obj, transform)
		{
				var html = $(document.createElement("li"));

				if (jQuery.type(obj) === 'object')
				{
					//Apply the transform to the object (name value pair)
					$(html).append( $.json2html.applyTransform(obj, transform) );
				}
				
				return(html);
		}

		$.json2html.applyTransform = function(obj,transform)
		{
			var html = $(document.createElement("div"));

            //If this is a function then run the function and add the elements returned

			//Itterate through the transform and create html as needed
			if (jQuery.type(transform) === "array")
			{	
				//Itterrate through the array and append it to the html object
				$(transform).each(function() {
								
					$(html).append( $.json2html.applyTransform(obj, this) );
				});

			} else if (jQuery.type(transform) === "object")
			{
				//Get the tag element of this transform
				if( transform["tag"] != null )
				{
					//Create a new element
					var element = $(document.createElement(transform["tag"]));
					
					//Add the html to the element (if we have one)
					if( transform["html"] != undefined ) $(element).html($.json2html.getValue(obj,transform,"html"));

					//Look into the properties of this transform
					for (var key in transform) 
					{
						//Add the property as a attribute if it's not a key one
						if( key != "tag" && key != "children" && key != "html")
						{
							if(key.indexOf("on") == 0) 
							{	
								var data = new Object();
								data.action = transform[key];
								data.obj = obj;
								data.data = $.json2html.options.eventData;

								$(element).bind(key.substring(key.indexOf("on")+2),data, function(event) 
								{
									data.event = event;
									data.action(data);
								});
								
							} else $(element).attr(key, $.json2html.getValue(obj, transform, key));
						}
					}

					//Append the children if we have any
					if( transform["children"] != undefined ) 
					{
					    if( jQuery.type(transform["children"]) === "function" ) $(element).append( transform["children"](obj) );
					    else $(element).append( $.json2html.applyTransform(obj, transform["children"]) );
					}

					//Return the newly created element
					html = element;
				}
			}
			
			return(html);
		}

		$.json2html.getValue = function(obj, transform, key)
		{
			var out = '';

			if( transform[key] != undefined )
			{
				//If this is a function then return the function with the obj
				if( jQuery.type(transform[key]) === "function" ) out = transform[key](obj);
				
				if (jQuery.type(transform[key]) === "string")
				{
					if (transform[key].length > 0)
				    {
					    //Check to see if this transform value is an object (must have a period to start)
					    if( transform[key][0] == '.' )
					    {
						    //Split the string into it's seperate components
						    var components = transform[key].split('.');

						    var useObj = obj;
    						
						    //Parse the object components
						    for (count=0;count<components.length;count++)
						    {
							    if( components[count].length > 0 )
							    {
								    var newObj = useObj[components[count]];
								    useObj = newObj;
								    if(useObj == null || useObj == undefined) break;
							    }
						    }

						    if(useObj != null && useObj != undefined) out = useObj;
					    } else out = transform[key];
					 }
				}
			}

			return(out);
		}

})(jQuery);