import { CommonModule } from "@angular/common";
import { FormsModule } from "@angular/forms";
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";
import { EditSettingComponent } from "./edit-setting-table/edit.component";
// Import our components
import { GisDiagramComponent } from "./gisDiagram.component";

// Define the routes for this Angular module
export const pluginRoutes: Routes = [
    {
        path: "",
        component: GisDiagramComponent,
    },
];

// Define the module
@NgModule({
    imports: [CommonModule, RouterModule.forChild(pluginRoutes), FormsModule],
    exports: [],
    providers: [],
    declarations: [GisDiagramComponent, EditSettingComponent],
})
export class GisDiagramModule {}
