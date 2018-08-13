/*!
 *   Copyright 2015 CityGrid Media, LLC
 *
 *   Licensed under the Apache License, Version 2.0 (the "License");
 *   you may not use this file except in compliance with the License.
 *   You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *   Unless required by applicable law or agreed to in writing, software
 *   distributed under the License is distributed on an "AS IS" BASIS,
 *   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *   See the License for the specific language governing permissions and
 *   limitations under the License.
 *
 */
$(document).ready(function() {

  $(".resizable1").resizable(
  {
      autoHide: false,
      handles: 's',
      minHeight: 70,
      containment: "#panel_c",
      resize: function(s, ui)
      {
          var parent = ui.element.parent();
          var remainingSpace = parent.height() - ui.element.outerHeight(),
              divTwo = ui.element.next(),
              divTwoHeight = (remainingSpace - (divTwo.outerHeight() - divTwo.height()))/parent.height()*100+"%";
              divTwo.height(divTwoHeight);
      },
      stop: function(s, ui)
      {
          var parent = ui.element.parent();
          ui.element.css(
          {
              height: ui.element.height()/parent.height()*100+"%",
          });
      }
  });
});
