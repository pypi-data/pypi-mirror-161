import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditBranchDetailComponent } from "./edit-branch-detail-table/edit.component";
import { EditSettingComponent } from "./edit-setting-table/edit.component";

// Import our components
import { BranchComponent } from "./branch.component";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: BranchComponent,
    },
];

// Define the module
@NgModule({
    imports: [CommonModule, RouterModule.forChild(pluginRoutes), FormsModule],
    exports: [],
    providers: [],
    declarations: [
        BranchComponent,
        EditBranchDetailComponent,
        EditSettingComponent,
    ],
})
export class BranchModule {}
