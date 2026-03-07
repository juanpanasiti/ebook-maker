-- Pandoc Lua filter: Adds line numbers to code blocks for EPUB output.
-- Each line gets a <span class="line-number">N</span> prefix.

function CodeBlock(el)
  local lines = {}
  local i = 1
  for line in el.text:gmatch("([^\n]*)\n?") do
    -- Avoid adding an extra empty line at the very end
    if i > 1 or line ~= "" then
      table.insert(lines, string.format(
        '<span class="line-number">%d</span>%s', i, escape_html(line)
      ))
      i = i + 1
    end
  end

  -- Remove trailing empty line that gmatch produces
  if #lines > 0 and lines[#lines]:match('^<span class="line%-number">%d+</span>$') then
    table.remove(lines, #lines)
  end

  local html = '<pre><code>' .. table.concat(lines, '\n') .. '</code></pre>'
  return pandoc.RawBlock('html', html)
end

function escape_html(s)
  s = s:gsub("&", "&amp;")
  s = s:gsub("<", "&lt;")
  s = s:gsub(">", "&gt;")
  s = s:gsub('"', "&quot;")
  return s
end
