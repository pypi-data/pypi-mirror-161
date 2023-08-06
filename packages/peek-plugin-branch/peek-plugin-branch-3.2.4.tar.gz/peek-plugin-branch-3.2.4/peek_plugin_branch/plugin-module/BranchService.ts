import { NgLifeCycleEvents, TupleSelector } from "@synerty/vortexjs";
import { branchTuplePrefix } from "./_private/PluginNames";
import { Injectable } from "@angular/core";
import { BranchDetailTuple } from "./BranchDetailTuple";
import { PrivateBranchTupleService } from "./_private/services/PrivateBranchTupleService";
import { CreateBranchActionTuple } from "./_private";

@Injectable()
export class BranchService extends NgLifeCycleEvents {
    public static readonly tupleName = branchTuplePrefix + "BranchDetailTable";

    constructor(private tupleService: PrivateBranchTupleService) {
        super();
    }

    createBranch(newBranch: BranchDetailTuple): Promise<void> {
        let action = new CreateBranchActionTuple();
        action.branchDetail = newBranch;
        let promise: any = this.tupleService.offlineAction.pushAction(action);
        return promise;
    }

    branches(modelSetKey: string): Promise<BranchDetailTuple[]> {
        let ts = new TupleSelector(BranchDetailTuple.tupleName, {
            modelSetKey: modelSetKey,
        });
        let promise: any =
            this.tupleService.offlineObserver.promiseFromTupleSelector(ts);
        return promise;
    }

    getBranch(
        modelSetKey: string,
        key: string
    ): Promise<BranchDetailTuple | null> {
        let ts = new TupleSelector(BranchDetailTuple.tupleName, {
            modelSetKey: modelSetKey,
        });
        let promise: any = this.tupleService.offlineObserver
            .promiseFromTupleSelector(ts)
            .then((branches: BranchDetailTuple[]) => {
                return branches.filter((b) => b.key == key)[0];
            });
        return promise;
    }
}
