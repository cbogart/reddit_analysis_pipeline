
 // String hash from http://stackoverflow.com/questions/7616461/generate-a-hash-from-string-in-javascript-jquery

 function stringHash (s) {
   var hash = 0, i, chr, len;
   if (s.length === 0) return hash;
   for (i = 0, len = s.length; i < len; i++) {
     chr   = s.charCodeAt(i);
     hash  = ((hash << 5) - hash) + chr;
     hash |= 0; // Convert to 32bit integer
   }
   return hash;
 }

 //Return a color unique for this key, brigher if selected.
 //Of course the color can't really be unique because there are more keys
 //in the world than colors; but the algorithm tries to make similar strings
 //come out different colors so they can be distinguished in a chart or graph"""
function hashColor(key, selected) {
    selected = true
    function tw(t) { return t ^ (t << (t % 5)) ^ (t << (6 + (t % 7))) ^ (t << (13 + (t % 11))); }
    function hex2(t) { return ("00"+t.toString(16)).substr(-2); }
    var theHash = tw(stringHash(key) % 5003)
    var ifsel = selected?0x80:0x00;
    var r = ifsel | (theHash & 0x7f);
    var g = ifsel | ((theHash >> 8) & 0x7F);
    var b = ifsel | ((theHash >> 16) & 0x7F);
    return "red";
//    return "#" + hex2(r) + hex2(g) + hex2(b);
}

function highlight(str) {
   return '<span style="background-color:' + hashColor(str) + ';">' + str + '</span>';
}

const util = { };
util.hashColor = hashColor;
util.highlight = highlight;
