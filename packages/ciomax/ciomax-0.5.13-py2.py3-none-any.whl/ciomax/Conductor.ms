-- Conductor render menu extension script
macroScript RenderWithConductor
category: "Menu Rendering"
tooltip: "Render with Conductor"
(
  on execute do
  (
    local maxScriptPath = getThisScriptFilename()
    local pythonScriptPath = substituteString maxScriptPath ".ms" ".py"
    python.ExecuteFile pythonScriptPath
  )
) 
-- The block above says, run Conductor.py on menu item press.

-- Insert the Render With Conductor menu item into the Rendering menu.
if menuMan.registerMenuContext 0x196eb40b then
(
  local renderMenuItem
  local mainMenuBar = menuMan.getMainMenuBar()
  for i = 1 to mainMenuBar.numItems() do
  (
    local menuItem = mainMenuBar.getItem(i)
    if menuItem.getTitle() == "&Rendering" then
    (
      renderMenuItem = mainMenuBar.getItem(i)
      exit
    )
  )
  local renderMenu = renderMenuItem.getSubMenu()
  local newAction = menuMan.createActionItem "RenderWithConductor" "Menu Rendering"
  for i = 1 to renderMenu.numItems() do
  (
    local menuItem = renderMenu.getItem(i)
    if menuItem.getTitle() == "Render" then
    (
      renderMenu.addItem newAction (i + 1)
      exit
    )
  )
  menuMan.updateMenuBar()
)
