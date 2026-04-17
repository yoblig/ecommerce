# process_calendar

## Purpose
Generate three HTML store hours files for a given month from input files in this folder.

## How to use
Drop input files (CSV, PDF, or PNG) into this folder, then ask:
> "Give me the HTML files for [Month]"

When asked to process a month, write all three HTML files immediately without asking for confirmation. Do not pause to confirm file writes — treat the request itself as full approval.

## Output files
| File | Location |
|------|----------|
| `[month]-sumc.html` | SUMC (Flagship) |
| `[month]-mckale.html` | The A-Store at McKale |
| `[month]-medical.html` | Health Sciences Campus Store (Medical) |

Use lowercase month name, e.g. `may-sumc.html`.

## HTML template per location

### SUMC
```html
<!-- Column 1 -->
<h3>Contact Information</h3>
<ul>
    <li><b>Phone</b> 520-621-2426</li>
    <li><b>Facsimile</b> 520-621-8098</li>
    <li>
        1209 E. University Blvd. <br>
        Tucson, Arizona, 85721-0019
    </li>
</ul>

<h3>Store Hours</h3>
<br/>
[HOURS — one line per day: Month D DayName: H:MMam–H:MMpm or CLOSED]
<br/>
<h3>Other Locations</h3>
<ul>
<li><a href="/mckale">The A-Store at McKale</a></li>
<li><a href="/medical">Campus Store Medical (Tucson)</a></li>
</ul>
```

### McKale
```html
<br></br>
<!-- Column 1 -->
<h3>Contact Information</h3>
<ul>
    <li><b>Phone: </b>520-621-2183</li>
    <li>1721 E. Enke Drive<br>
        Tucson, Arizona, 85720
        <br>
    </li>
</ul>

<h3>Store Hours</h3>
<br/>
[HOURS — one line per day: Month D DayName: H:MMam–H:MMpm or CLOSED]

<br/><br/>
<h3>Other Locations</h3>
<ul>
    <li><a href="/sumc">SUMC (Flagship Store)</a></li>
    <li><a href="/medical">Health Sciences Campus Store (Medical)</a></li>
</ul>
```

### Medical
```html
<br></br>
<!-- Column 1 -->
<h3>Contact Information</h3>
<ul>
    <li><b>Phone</b> 520-626-6669</li>

    <li>
        1501 N. Campbell Ave. #1116 <br>
        Tucson, Arizona, 85724-0019
    </li>
</ul>
<h3>Store Hours</h3>
[HOURS — one line per day: Month D DayName: H:MMam–H:MMpm or CLOSED]
<br/>
<h3>Other Locations</h3>
<ul>
<li><a href="/sumc">SUMC (Flagship Store)</a></li>
<li><a href="/mckale">The A-Store at McKale</a></li>
</ul>
```

## Hours format
Each day is one line:
```
Month D DayName: H:MMam–H:MMpm<br/>
```
- Use `CLOSED` (all caps) when the store is closed
- Use `am`/`pm` lowercase, no space before (e.g. `10am`, `7:30am`)
- Use an en dash `–` between open and close times
- Every day of the month must be listed, in order

## Input file conventions
- Input files may be CSV, PDF, or PNG
- A file with `sumc` in the name covers the SUMC location
- A file with `mckale` in the name covers McKale
- A file with `medical` in the name covers Medical
- Some files may cover multiple locations (e.g. a CSV with McKale and Medical columns)
- PDFs and PNGs are typically monthly calendar grids — read them visually and extract each day's hours
