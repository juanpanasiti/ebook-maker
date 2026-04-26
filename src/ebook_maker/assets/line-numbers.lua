-- Pandoc Lua filter: Adds line numbers to code blocks by leveraging Pandoc's native highlighting
-- By adding the 'numberLines' class, Pandoc's Skylighting engine will automatically generate 
-- line numbers alongside syntax highlighting.

function CodeBlock(el)
  -- Check if it already has numberLines to avoid duplicates
  local has_numbers = false
  for _, class in ipairs(el.classes) do
    if class == "numberLines" then
      has_numbers = true
      break
    end
  end

  -- Add the native pandoc class for numbering lines
  if not has_numbers then
    table.insert(el.classes, "numberLines")
  end

  return el
end
