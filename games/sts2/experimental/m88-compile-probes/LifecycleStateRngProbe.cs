using MegaCrit.Sts2.Core.Entities.Cards;
using MegaCrit.Sts2.Core.Entities.Players;
using MegaCrit.Sts2.Core.Models;
using MegaCrit.Sts2.Core.Runs;
using STS2RitsuLib;
using STS2RitsuLib.Data;
using STS2RitsuLib.Models.Capabilities;
using STS2RitsuLib.RunData;
using STS2RitsuLib.Utils;
using STS2RitsuLib.Utils.Persistence;

namespace M88CompileProbes;

public sealed class SharedState
{
    public int Count { get; set; }
}

public static class LifecycleStateRngProbe
{
    private static readonly AttachedState<object, SharedState> RuntimeState = new(() => new());
    private static readonly SavedAttachedState<CardModel, int> SavedCardState =
        new("m88_saved_card", () => 0);

    private static RunSavedData<SharedState> _runState = null!;
    private static PlayerRunSavedData<SharedState> _playerState = null!;
    private static ModelSavedData<CardModel, SharedState> _modelState = null!;
    private static ModDataStoreCache<SharedState> _profileCache = null!;

    public static void Register(string modId)
    {
        using (RitsuLibFramework.BeginModDataRegistration(modId))
        {
            var runStore = RitsuLibFramework.GetRunSavedDataStore(modId);
            _runState = runStore.Register("m88_run", () => new SharedState(), new()
            {
                WritePolicy = RunSavedDataWritePolicy.WhenNonDefault,
                SyncLobbyOnChange = false,
            });
            _playerState = runStore.RegisterPerPlayer("m88_player", () => new SharedState(), new()
            {
                WritePolicy = RunSavedDataWritePolicy.WhenSet,
                SyncLobbyOnChange = false,
            });

            _modelState = RitsuLibFramework.GetModelSavedDataStore(modId)
                .Register<CardModel, SharedState>("m88_model", () => new SharedState(), new()
                {
                    WritePolicy = ModelSavedDataWritePolicy.WhenNonDefault,
                    ClonePolicy = ModelSavedDataClonePolicy.Copy,
                });

            var dataStore = RitsuLibFramework.GetDataStore(modId);
            dataStore.Register<SharedState>(
                "m88_profile",
                "m88-profile.json",
                SaveScope.Profile,
                syncToCloud: false,
                defaultFactory: () => new SharedState());
            _profileCache = dataStore.CreateCache<SharedState>("m88_profile");
        }

        _ = RitsuLibFramework.SubscribeLifecycle<CombatStartingEvent>(_ => { }, false);
        _ = RitsuLibFramework.SubscribeLifecycleOnce<GameReadyEvent>(_ => { }, true);
    }

    public static void Exercise(
        object runtimeOwner,
        CardModel card,
        RunState runState,
        Player player,
        string modId)
    {
        RuntimeState.Update(runtimeOwner, state =>
        {
            state.Count++;
            return state;
        });
        SavedCardState[card]++;
        _modelState.Modify(card, static state => state.Count++);
        _runState.Modify(runState, static state => state.Count++);
        _playerState.Modify(player, static state => state.Count++);
        _profileCache.Modify(static state => state.Count++);
        _profileCache.Save();

        _ = RitsuLibFramework.GetModRunRng(runState, modId, "shared");
        _ = RitsuLibFramework.GetModRunRng(player, modId, "shared");
        _ = RitsuLibFramework.GetModPlayerRng(player, modId, "per-player");
    }
}
