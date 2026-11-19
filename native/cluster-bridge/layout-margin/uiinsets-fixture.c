#include "wire-margin.c"
#include "vectors.h"
#include "uiinsets-vectors.h"
#include <stdio.h>
#define CHECK(x) do { if(!(x)) { fprintf(stderr,"UIINSETS_FIXTURE_FAIL line=%d\n",__LINE__); return 1; } } while(0)
#define REJECT(a) do { n=99; CHECK(!cluster_wire_rewrite(a,sizeof(a),out,sizeof(out),&n)&&!n); } while(0)
int main(void)
{
    unsigned n; unsigned char out[16384],in[8192];
    (void)expected; (void)extra_expected;
    CHECK(LAYOUT_UI_INSET_PIXELS==120 && LAYOUT_UI_TOP_INSET_PIXELS==8 && LAYOUT_UI_BOTTOM_INSET_PIXELS==96 && LAYOUT_UI_STABLE_BOTTOM_INSET_PIXELS==64 && MARGIN_WIDTH_PIXELS==0 && LAYOUT_DENSITY_DPI==140);
    CHECK((LAYOUT_UI_TOP_INSET_PIXELS+480-LAYOUT_UI_BOTTOM_INSET_PIXELS)/2==196);
    CHECK(layout_metadata_rewrite(input,sizeof input,out,sizeof out,&n) && n==sizeof baseline && !memcmp(out,baseline,n));
    CHECK(cluster_wire_rewrite(input,sizeof input,out,sizeof out,&n) && n==sizeof ui_expected && !memcmp(out,ui_expected,n));
    CHECK(cluster_wire_rewrite(extra_input,sizeof extra_input,out,sizeof out,&n) && n==sizeof ui_extra_expected && !memcmp(out,ui_extra_expected,n));
    REJECT(bad_wire); REJECT(nonzero_width); REJECT(duplicate_width); REJECT(missing_width);
    REJECT(ui_present); REJECT(ui_duplicate); REJECT(ui_bad_wire); REJECT(ui_bad_nested);
    n=99; CHECK(!cluster_wire_rewrite(input,sizeof input,out,7,&n)&&!n);
    n=99; CHECK(!cluster_wire_rewrite(input,sizeof input,out,sizeof ui_expected-1,&n)&&!n);
    memcpy(in,input,sizeof input);n=99;
    CHECK(!cluster_wire_rewrite(in,sizeof input,in,sizeof in,&n)&&!n&&!memcmp(in,input,sizeof input));
    CHECK(!cluster_wire_rewrite(input,sizeof input,out,sizeof out,0));
    puts("CLUSTER_UI_INSETS_QNX_PASS width_total=0 height_total=0 dpi=140 resolution=800x480 inset_left=120 inset_right=120 inset_top=8 inset_bottom=96 stable_bottom=64 center_y=196 secondary_only=1 primary_unchanged=1 unknown_preserved=1 existing_ui_refused=1 malformed_refused=1 bounds=1");
    return 0;
}
